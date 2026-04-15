"""
Data Source Layer - Veri Kaynağından Bağımsız Mimari
Tüm veri kaynakları (Live Wi-Fi, CSV Dataset, CSV Replay) tek bir interface üzerinden çalışır.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any
import pandas as pd
import time
from pathlib import Path


class FlowData:
    """Normalize edilmiş flow verisi - tüm kaynaklardan aynı format"""
    
    def __init__(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        proto: str,
        duration: float,
        packets_fwd: int = 0,
        packets_bwd: int = 0,
        bytes_fwd: int = 0,
        bytes_bwd: int = 0,
        syn: int = 0,
        ack: int = 0,
        rst: int = 0,
        fin: int = 0,
        unique_dst_ports: int = 0,
        timestamp: Optional[float] = None,
        label: Optional[int] = None,
        attack_type: Optional[str] = None,
        **kwargs
    ):
        self.src_ip = str(src_ip)
        self.dst_ip = str(dst_ip)
        self.src_port = int(src_port or 0)
        self.dst_port = int(dst_port or 0)
        self.proto = str(proto or "IP")
        self.duration = float(duration or 0.0)
        self.packets_fwd = int(packets_fwd or 0)
        self.packets_bwd = int(packets_bwd or 0)
        self.bytes_fwd = int(bytes_fwd or 0)
        self.bytes_bwd = int(bytes_bwd or 0)
        self.syn = int(syn or 0)
        self.ack = int(ack or 0)
        self.rst = int(rst or 0)
        self.fin = int(fin or 0)
        self.unique_dst_ports = int(unique_dst_ports or 0)
        self.timestamp = timestamp or time.time()
        self.label = label  # 0=normal, 1=attack (optional)
        self.attack_type = attack_type  # optional
        self.extra = kwargs  # ekstra alanlar
        
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatına çevir"""
        d = {
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "proto": self.proto,
            "duration": self.duration,
            "packets_fwd": self.packets_fwd,
            "packets_bwd": self.packets_bwd,
            "bytes_fwd": self.bytes_fwd,
            "bytes_bwd": self.bytes_bwd,
            "syn": self.syn,
            "ack": self.ack,
            "rst": self.rst,
            "fin": self.fin,
            "unique_dst_ports": self.unique_dst_ports,
            "timestamp": self.timestamp,
        }
        if self.label is not None:
            d["label"] = self.label
        if self.attack_type:
            d["attack_type"] = self.attack_type
        d.update(self.extra)
        return d
    
    def to_flow_dict(self) -> Dict[str, Any]:
        """Live agent için uyumlu format"""
        return {
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "proto": self.proto,
            "duration": self.duration,
            "packets_fwd": self.packets_fwd,
            "packets_bwd": self.packets_bwd,
            "bytes_fwd": self.bytes_fwd,
            "bytes_bwd": self.bytes_bwd,
            "syn": self.syn,
            "ack": self.ack,
            "rst": self.rst,
            "fin": self.fin,
            "unique_dst_ports": self.unique_dst_ports,
            "pps": (self.packets_fwd + self.packets_bwd) / max(self.duration, 0.001),
        }


class DataSource(ABC):
    """Tüm veri kaynakları için base class"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Veri kaynağının adı"""
        pass
    
    @abstractmethod
    def get_flows(self) -> Iterator[FlowData]:
        """Flow verilerini iterator olarak döndürür"""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Kaynak aktif mi?"""
        pass


class LiveWiFiSource(DataSource):
    """Canlı Wi-Fi trafik kaynağı"""
    
    def __init__(self, flow_aggregator):
        self.flow_aggregator = flow_aggregator
        self._active = True
    
    def get_name(self) -> str:
        return "LIVE"
    
    def is_active(self) -> bool:
        return self._active
    
    def get_flows(self) -> Iterator[FlowData]:
        """Flow aggregator'dan gelen flow'ları normalize et"""
        while self._active:
            flows = self.flow_aggregator.flush()
            for flow_dict in flows:
                yield FlowData(
                    src_ip=flow_dict.get("src_ip", ""),
                    dst_ip=flow_dict.get("dst_ip", ""),
                    src_port=flow_dict.get("src_port", 0),
                    dst_port=flow_dict.get("dst_port", 0),
                    proto=flow_dict.get("proto", "IP"),
                    duration=flow_dict.get("duration", 0.0),
                    packets_fwd=flow_dict.get("packets_fwd", 0),
                    packets_bwd=flow_dict.get("packets_bwd", 0),
                    bytes_fwd=flow_dict.get("bytes_fwd", 0),
                    bytes_bwd=flow_dict.get("bytes_bwd", 0),
                    syn=flow_dict.get("syn", 0),
                    ack=flow_dict.get("ack", 0),
                    rst=flow_dict.get("rst", 0),
                    fin=flow_dict.get("fin", 0),
                    unique_dst_ports=flow_dict.get("unique_dst_ports", 0),
                )
            time.sleep(0.1)  # CPU kullanımını azalt
    
    def stop(self):
        self._active = False


class CSVDatasetSource(DataSource):
    """CSV dataset kaynağı - offline test için (Memory-safe chunk-based processing)"""
    
    def __init__(
        self, 
        csv_path: str, 
        label_col: str = "label", 
        attack_type_col: Optional[str] = "attack_cat",
        max_samples: Optional[int] = 10000,  # Limit samples for memory safety
        chunk_size: int = 1000,  # Process in chunks
        use_stratified_sampling: bool = True  # Use stratified sampling for balanced attack types
    ):
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV dosyası bulunamadı: {csv_path}")
        
        self.label_col = label_col
        self.attack_type_col = attack_type_col
        self.max_samples = max_samples
        self.chunk_size = chunk_size
        self.use_stratified_sampling = use_stratified_sampling
        self._chunk_iterator = None
        self._current_chunk: Optional[pd.DataFrame] = None
        self._chunk_idx = 0
        self._row_idx = 0
        self._total_processed = 0
        self._total_rows = None  # Total row count for progress calculation
        self._shuffled_data = None  # Pre-shuffled data for balanced distribution
        self._shuffled_idx = 0
        self._initialize_reader()
    
    def _initialize_reader(self):
        """CSV reader'ı başlat (chunk-based, shuffled for balanced distribution)"""
        print(f"[CSV Dataset] Yükleniyor (chunk-based, shuffled): {self.csv_path}")
        print(f"[CSV Dataset] Max samples: {self.max_samples}, Chunk size: {self.chunk_size}")
        
        # Estimate total rows (for progress calculation)
        try:
            # Quick row count estimation (read first chunk to get structure)
            sample_chunk = pd.read_csv(self.csv_path, nrows=100, low_memory=True)
            # Count total rows (this is approximate, but fast)
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Count lines (approximate, includes header)
                line_count = sum(1 for _ in f)
                self._total_rows = max(1, line_count - 1)  # Subtract header
            print(f"[CSV Dataset] Estimated total rows: {self._total_rows:,}")
        except Exception as e:
            print(f"[CSV Dataset] Could not estimate total rows: {e}")
            self._total_rows = None
        
        # Stratified sampling için: Tüm veri setini okuyup shuffle et (memory-safe değil ama balanced)
        # Alternatif: Chunk-based ama daha iyi shuffle
        if self.use_stratified_sampling and self.max_samples:
            try:
                print(f"[CSV Dataset] Stratified sampling aktif: Tüm attack type'larından balanced örnek alınıyor...")
                # Tüm veri setini oku (memory-safe değil ama balanced distribution için gerekli)
                df_full = pd.read_csv(
                    self.csv_path,
                    low_memory=True,
                    dtype={
                        'Destination Port': 'float32',
                        'Flow Duration': 'float32',
                        'Total Fwd Packets': 'float32',
                        'Total Length of Fwd Packets': 'float32',
                        'Total Bwd Packets': 'float32',
                        'Total Length of Bwd Packets': 'float32',
                    }
                )
                
                # Label kolonunu bul
                label_col_name = self.label_col if self.label_col in df_full.columns else "Label"
                if label_col_name not in df_full.columns:
                    label_col_name = "Label" if "Label" in df_full.columns else None
                
                if label_col_name:
                    # Tüm attack type'ları göster
                    unique_labels = df_full[label_col_name].unique()
                    print(f"[CSV Dataset] Veri setinde bulunan attack type'lar: {list(unique_labels)}")
                    print(f"[CSV Dataset] Attack type sayısı: {len(unique_labels)}")
                    
                    # Her attack type'tan eşit sayıda örnek al (stratified sampling)
                    num_classes = df_full[label_col_name].nunique()
                    if num_classes > 0:
                        samples_per_class = self.max_samples // num_classes
                        # Minimum her class'tan en az 2000 örnek al (daha iyi dağılım için)
                        # Böylece tüm attack type'lar görünecek
                        samples_per_class = max(2000, samples_per_class)
                        print(f"[CSV Dataset] Her attack type'tan ~{samples_per_class} örnek alınacak")
                    else:
                        samples_per_class = self.max_samples
                    
                    # Stratified sampling - Her class'tan eşit sayıda
                    df_sampled_list = []
                    for label_val in unique_labels:
                        label_df = df_full[df_full[label_col_name] == label_val]
                        if len(label_df) > 0:
                            # Her class'tan samples_per_class kadar al (veya mevcut olan kadar)
                            sample_size = min(len(label_df), samples_per_class)
                            sampled = label_df.sample(n=sample_size, random_state=42)
                            df_sampled_list.append(sampled)
                            print(f"[CSV Dataset] {label_val}: {sample_size} örnek alındı (toplam: {len(label_df)})")
                    
                    # Tüm class'ları birleştir
                    if df_sampled_list:
                        df_sampled = pd.concat(df_sampled_list, ignore_index=True)
                    else:
                        df_sampled = df_full.head(self.max_samples)
                    
                    # Shuffle tüm veri seti (karışık dağılım için)
                    df_sampled = df_sampled.sample(frac=1.0, random_state=42).reset_index(drop=True)
                    
                    # Limit to max_samples (eğer aşıldıysa)
                    if len(df_sampled) > self.max_samples:
                        df_sampled = df_sampled.head(self.max_samples)
                    
                    print(f"[CSV Dataset] Stratified sampling tamamlandı: {len(df_sampled)} örnek")
                    print(f"[CSV Dataset] Final attack type dağılımı:")
                    if label_col_name in df_sampled.columns:
                        print(df_sampled[label_col_name].value_counts())
                    
                    # Shuffled data'yı sakla
                    self._shuffled_data = df_sampled
                    self._shuffled_idx = 0
                    self._current_chunk = None
                    self._chunk_iterator = None
                    return
                else:
                    print(f"[CSV Dataset] Label kolonu bulunamadı, normal chunk-based okuma kullanılıyor")
            except Exception as e:
                print(f"[CSV Dataset] Stratified sampling hatası: {e}, normal chunk-based okuma kullanılıyor")
                import traceback
                traceback.print_exc()
        
        # Normal chunk-based reader (fallback veya stratified sampling kapalıysa)
        self._chunk_iterator = pd.read_csv(
            self.csv_path,
            chunksize=self.chunk_size,
            dtype={
                # Numeric columns as float32 to save memory
                'Destination Port': 'float32',
                'Flow Duration': 'float32',
                'Total Fwd Packets': 'float32',
                'Total Length of Fwd Packets': 'float32',
                'Total Bwd Packets': 'float32',
                'Total Length of Bwd Packets': 'float32',
            },
            low_memory=True
        )
        
        # İlk chunk'ı yükle ve shuffle et (balanced distribution için)
        try:
            self._current_chunk = next(self._chunk_iterator)
            # Shuffle chunk içindeki satırları (sıralı okuma bias'ını önlemek için)
            self._current_chunk = self._current_chunk.sample(frac=1.0, random_state=42).reset_index(drop=True)
            self._chunk_idx = 0
            self._row_idx = 0
            print(f"[CSV Dataset] İlk chunk yüklendi ve shuffle edildi: {len(self._current_chunk)} satır")
        except StopIteration:
            self._current_chunk = None
            print("[CSV Dataset] Dosya boş")
    
    def _load_next_chunk(self) -> bool:
        """Sonraki chunk'ı yükle ve shuffle et"""
        if self._chunk_iterator is None:
            return False
        
        try:
            self._current_chunk = next(self._chunk_iterator)
            # Shuffle chunk içindeki satırları (balanced distribution için)
            self._current_chunk = self._current_chunk.sample(frac=1.0, random_state=42 + self._chunk_idx).reset_index(drop=True)
            self._chunk_idx += 1
            self._row_idx = 0
            return True
        except StopIteration:
            self._current_chunk = None
            return False
    
    def get_name(self) -> str:
        return "DATASET"
    
    def is_active(self) -> bool:
        """Hala işlenecek veri var mı?"""
        if self.max_samples and self._total_processed >= self.max_samples:
            return False
        
        # Stratified sampling kullanılıyorsa
        if self._shuffled_data is not None:
            return self._shuffled_idx < len(self._shuffled_data)
        
        # Normal chunk-based
        return self._current_chunk is not None and self._row_idx < len(self._current_chunk)
    
    def _row_to_flow(self, row) -> Optional[FlowData]:
        """Bir satırı FlowData'ya dönüştür (helper method)"""
        # Kolon isimlerini bir kez al
        cols_lower = {col.lower(): col for col in row.index if hasattr(row, 'index')}
        
        def get_col_value(row, possible_names, default=""):
            """Kolon ismini bul ve değeri al"""
            for name in possible_names:
                if name in row.index:
                    val = row[name]
                    if isinstance(val, (float, int)) and not pd.isna(val):
                        return float(val)
                    return val if pd.notna(val) else default
                name_lower = name.lower()
                if name_lower in cols_lower:
                    actual_col = cols_lower[name_lower]
                    val = row[actual_col]
                    if isinstance(val, (float, int)) and not pd.isna(val):
                        return float(val)
                    return val if pd.notna(val) else default
            return default
        
        # IP bilgileri
        row_idx_mod = self._total_processed % 255
        src_ip = get_col_value(row, [
            "srcip", "src_ip", "sourceip", "source_ip", 
            "Source IP", "SourceIP"
        ], f"10.0.0.{row_idx_mod}")
        dst_ip = get_col_value(row, [
            "dstip", "dst_ip", "destip", "destinationip",
            "Destination IP", "DestinationIP"
        ], f"10.0.1.{row_idx_mod}")
        
        # Port bilgileri
        src_port = int(get_col_value(row, [
            "sport", "src_port", "sourceport", "Source Port", "SourcePort"
        ], 0) or 0)
        dst_port = int(get_col_value(row, [
            "dsport", "dst_port", "destport", "destinationport",
            "Destination Port", "DestinationPort"
        ], 0) or 0)
        
        # Protocol
        proto_raw = get_col_value(row, [
            "proto", "protocol", "proto_name", "Protocol"
        ], "tcp")
        proto = str(proto_raw).upper() if proto_raw else "IP"
        
        # Duration
        duration = float(get_col_value(row, [
            "dur", "duration", "Flow Duration", "FlowDuration"
        ], 0.0) or 0.0)
        
        # Packets
        packets_fwd = int(get_col_value(row, [
            "spkts", "packets_fwd", "srcpkts",
            "Total Fwd Packets", "TotalFwdPackets", "Fwd Packets"
        ], 0) or 0)
        packets_bwd = int(get_col_value(row, [
            "dpkts", "packets_bwd", "dstpkts",
            "Total Bwd Packets", "TotalBwdPackets", "Bwd Packets"
        ], 0) or 0)
        
        # Bytes
        bytes_fwd = int(get_col_value(row, [
            "sbytes", "bytes_fwd", "srcbytes",
            "Total Length of Fwd Packets", "TotalLengthofFwdPackets",
            "Fwd Packet Length Total"
        ], 0) or 0)
        bytes_bwd = int(get_col_value(row, [
            "dbytes", "bytes_bwd", "dstbytes",
            "Total Length of Bwd Packets", "TotalLengthofBwdPackets",
            "Bwd Packet Length Total"
        ], 0) or 0)
        
        # Label ve attack type (aynı mantık)
        label = None
        attack_type = None
        
        # CICIDS2018 formatını kontrol et
        if "Label" in row.index:
            label_val = row["Label"]
            if pd.notna(label_val):
                label_str = str(label_val).strip()
                label_lower = label_str.lower()
                if label_lower in ["benign", "normal", "normal traffic", "0"]:
                    label = 0
                    attack_type = "NORMAL"
                else:
                    label = 1
                    attack_type = label_str
        
        # CICIDS 2017 formatını kontrol et
        if attack_type is None and "Attack Type" in row.index:
            at_val = row["Attack Type"]
            if pd.notna(at_val):
                attack_type = str(at_val).strip()
                at_lower = attack_type.lower()
                if at_lower in ["normal traffic", "normal", "benign"]:
                    label = 0
                    attack_type = "NORMAL"
                else:
                    label = 1
        
        # UNSW-NB15 formatı (label ve attack_cat)
        if label is None:
            if self.label_col and self.label_col in row.index:
                label_val = row[self.label_col]
                if pd.notna(label_val):
                    try:
                        label = int(label_val)
                    except:
                        label = 1 if str(label_val).lower() not in ["0", "normal", "benign"] else 0
        
        # Attack type from attack_cat (UNSW-NB15) or attack_type_col
        if attack_type is None and self.attack_type_col:
            if self.attack_type_col in row.index:
                at_val = row[self.attack_type_col]
                if pd.notna(at_val):
                    attack_type = str(at_val).strip()
            elif "attack_cat" in row.index:
                at_val = row["attack_cat"]
                if pd.notna(at_val):
                    attack_type = str(at_val).strip()
        
        # Attack type normalize
        if attack_type:
            attack_type = attack_type.strip()
            at_lower = attack_type.lower()
            if at_lower in ["normal", "benign", "normal traffic", "0", ""]:
                attack_type = "NORMAL"
                if label is None:
                    label = 0
            else:
                if label is None:
                    label = 1
        
        try:
            return FlowData(
                src_ip=str(src_ip),
                dst_ip=str(dst_ip),
                src_port=src_port,
                dst_port=dst_port,
                proto=proto,
                duration=duration,
                packets_fwd=packets_fwd,
                packets_bwd=packets_bwd,
                bytes_fwd=bytes_fwd,
                bytes_bwd=bytes_bwd,
                label=label,
                attack_type=attack_type,
                timestamp=time.time()
            )
        except Exception as e:
            print(f"[CSV Dataset] FlowData oluşturma hatası: {e}")
            return None
    
    def get_flows(self) -> Iterator[FlowData]:
        """CSV'den flow'ları oku ve normalize et (chunk-based veya stratified sampling)"""
        # Stratified sampling kullanılıyorsa
        if self._shuffled_data is not None:
            while self._shuffled_idx < len(self._shuffled_data):
                if self.max_samples and self._total_processed >= self.max_samples:
                    return
                
                row = self._shuffled_data.iloc[self._shuffled_idx]
                self._shuffled_idx += 1
                self._total_processed += 1
                
                flow = self._row_to_flow(row)
                if flow:
                    yield flow
            return
        
        # Normal chunk-based okuma
        if self._current_chunk is None:
            return
        
        # Kolon isimlerini bir kez al (chunk'tan)
        cols_lower = {col.lower(): col for col in self._current_chunk.columns}
        
        def get_col_value(row, possible_names, default=""):
            """Kolon ismini bul ve değeri al"""
            for name in possible_names:
                if name in row.index:
                    val = row[name]
                    # float64'ü float32'ye çevir (memory saving)
                    if isinstance(val, (float, int)) and not pd.isna(val):
                        return float(val)
                    return val if pd.notna(val) else default
                # Case-insensitive arama
                name_lower = name.lower()
                if name_lower in cols_lower:
                    actual_col = cols_lower[name_lower]
                    val = row[actual_col]
                    if isinstance(val, (float, int)) and not pd.isna(val):
                        return float(val)
                    return val if pd.notna(val) else default
            return default
        
        # Chunk-based processing
        while self._current_chunk is not None:
            # Mevcut chunk'taki satırları işle
            while self._row_idx < len(self._current_chunk):
                # Max samples kontrolü
                if self.max_samples and self._total_processed >= self.max_samples:
                    print(f"[CSV Dataset] Max samples ({self.max_samples}) ulaşıldı, durduruluyor...")
                    return
                
                row = self._current_chunk.iloc[self._row_idx]
                self._row_idx += 1
                self._total_processed += 1
                
                # _row_to_flow helper metodunu kullan
                flow = self._row_to_flow(row)
                if flow:
                    yield flow
                
                # Sonraki chunk'a geç
                if self._row_idx >= len(self._current_chunk):
                    if not self._load_next_chunk():
                        break
                continue
                
                # Eski kod (artık kullanılmıyor, _row_to_flow kullanılıyor)
                # IP bilgileri (CICIDS 2017'de IP yok, dummy IP kullan)
                row_idx_mod = self._total_processed % 255
                src_ip = get_col_value(row, [
                    "srcip", "src_ip", "sourceip", "source_ip", 
                    "Source IP", "SourceIP"
                ], f"10.0.0.{row_idx_mod}")
                dst_ip = get_col_value(row, [
                    "dstip", "dst_ip", "destip", "destinationip",
                    "Destination IP", "DestinationIP"
                ], f"10.0.1.{row_idx_mod}")
                
                # Port bilgileri (CICIDS 2017: "Destination Port")
                src_port = int(get_col_value(row, [
                    "sport", "src_port", "sourceport", "Source Port", "SourcePort"
                ], 0) or 0)
                dst_port = int(get_col_value(row, [
                    "dsport", "dst_port", "destport", "destinationport",
                    "Destination Port", "DestinationPort"
                ], 0) or 0)
                
                # Protocol (CICIDS 2017'de yok, varsayılan)
                proto_raw = get_col_value(row, [
                    "proto", "protocol", "proto_name", "Protocol"
                ], "tcp")
                proto = str(proto_raw).upper() if proto_raw else "IP"
                
                # Duration (CICIDS 2017: "Flow Duration") - float32
                duration = float(get_col_value(row, [
                    "dur", "duration", "Flow Duration", "FlowDuration"
                ], 0.0) or 0.0)
                
                # Packets (CICIDS 2017: "Total Fwd Packets", "Total Bwd Packets")
                packets_fwd = int(get_col_value(row, [
                    "spkts", "packets_fwd", "srcpkts",
                    "Total Fwd Packets", "TotalFwdPackets", "Fwd Packets"
                ], 0) or 0)
                packets_bwd = int(get_col_value(row, [
                    "dpkts", "packets_bwd", "dstpkts",
                    "Total Bwd Packets", "TotalBwdPackets", "Bwd Packets"
                ], 0) or 0)
                
                # Bytes (CICIDS 2017: "Total Length of Fwd Packets", "Total Length of Bwd Packets")
                bytes_fwd = int(get_col_value(row, [
                    "sbytes", "bytes_fwd", "srcbytes",
                    "Total Length of Fwd Packets", "TotalLengthofFwdPackets",
                    "Fwd Packet Length Total"
                ], 0) or 0)
                bytes_bwd = int(get_col_value(row, [
                    "dbytes", "bytes_bwd", "dstbytes",
                    "Total Length of Bwd Packets", "TotalLengthofBwdPackets",
                    "Bwd Packet Length Total"
                ], 0) or 0)
                
                # Label ve attack type
                label = None
                attack_type = None
                
                # CICIDS2018 formatını kontrol et (Label kolonu string değerler içerir: "Benign", "FTP-BruteForce", "SSH-Bruteforce", etc.)
                if "Label" in row.index:
                    label_val = row["Label"]
                    if pd.notna(label_val):
                        label_str = str(label_val).strip()
                        label_lower = label_str.lower()
                        # CICIDS2018: "Benign" = normal, diğerleri = attack
                        if label_lower in ["benign", "normal", "normal traffic", "0"]:
                            label = 0
                            attack_type = "NORMAL"
                        else:
                            label = 1
                            # PRESERVE original CICIDS2018 attack name (FTP-BruteForce, SSH-Bruteforce, etc.)
                            attack_type = label_str  # Keep as-is: "FTP-BruteForce", "SSH-Bruteforce", etc.
                
                # CICIDS 2017 formatını kontrol et (Attack Type kolonu)
                if attack_type is None and "Attack Type" in row.index:
                    at_val = row["Attack Type"]
                    if pd.notna(at_val):
                        attack_type = str(at_val).strip()
                        # CICIDS 2017: "Normal Traffic" = 0, diğerleri = 1
                        at_lower = attack_type.lower()
                        if at_lower in ["normal traffic", "normal", "benign"]:
                            label = 0
                            attack_type = "NORMAL"
                        else:
                            label = 1
                            # PRESERVE original attack name (DoS Hulk, PortScan, DDoS, Web Attack, etc.)
                            attack_type = attack_type  # Keep as-is (e.g., "DoS Hulk", "PortScan", "DDoS", "Web Attack")
                
                # UNSW-NB15 formatı için (eğer CICIDS formatları değilse)
                if label is None:
                    if self.label_col and self.label_col in row.index:
                        label_val = row[self.label_col]
                        if pd.notna(label_val):
                            try:
                                label = int(label_val)
                            except:
                                # String ise (örn: "0", "1")
                                label = 1 if str(label_val).lower() not in ["0", "normal", "benign"] else 0
                    elif "label" in row.index and "Label" not in row.index:  # lowercase label (UNSW-NB15)
                        label_val = row["label"]
                        if pd.notna(label_val):
                            try:
                                label = int(label_val)
                            except:
                                label = 1 if str(label_val).lower() not in ["0", "normal", "benign"] else 0
                
                # UNSW-NB15 attack type (eğer CICIDS formatlarında yoksa)
                if attack_type is None and self.attack_type_col:
                    if self.attack_type_col in row.index:
                        at_val = row[self.attack_type_col]
                        if pd.notna(at_val):
                            attack_type = str(at_val).strip()
                    elif "attack_cat" in row.index:
                        at_val = row["attack_cat"]
                        if pd.notna(at_val):
                            attack_type = str(at_val).strip()
                
                # Attack type'ı normalize et - PRESERVE original attack names
                # Do NOT collapse to generic - keep exact attack type names from dataset
                if attack_type:
                    attack_type = attack_type.strip()
                    at_lower = attack_type.lower()
                    if at_lower in ["normal", "benign", "normal traffic", "0", ""]:
                        attack_type = "NORMAL"
                        if label is None:
                            label = 0
                    else:
                        # PRESERVE original attack name exactly as in dataset
                        # Examples: "DoS Hulk", "FTP-BruteForce", "PortScan", "Bot", "DDoS", 
                        # "Web Attack", "SSH-Bruteforce", "FTP-Patator", etc.
                        # Do NOT convert to uppercase, do NOT collapse to generic
                        attack_type = attack_type  # Keep original format exactly
                        if label is None:
                            label = 1
                
                yield FlowData(
                    src_ip=str(src_ip),
                    dst_ip=str(dst_ip),
                    src_port=src_port,
                    dst_port=dst_port,
                    proto=proto,
                    duration=float(duration),  # float32
                    packets_fwd=packets_fwd,
                    packets_bwd=packets_bwd,
                    bytes_fwd=bytes_fwd,
                    bytes_bwd=bytes_bwd,
                    syn=0,  # CSV'de yoksa 0
                    ack=0,
                    rst=0,
                    fin=0,
                    unique_dst_ports=0,
                    label=label,
                    attack_type=attack_type,
                )
            
            # Chunk bitti, sonraki chunk'ı yükle
            if not self._load_next_chunk():
                break
        
        print(f"[CSV Dataset] Toplam {self._total_processed} satır işlendi")
    
    def reset(self):
        """Başa dön"""
        self._initialize_reader()


class CSVReplaySource(DataSource):
    """CSV Replay kaynağı - canlı simülasyon"""
    
    def __init__(
        self, 
        csv_source: CSVDatasetSource, 
        replay_speed: float = 1.0
    ):
        """
        replay_speed: 1.0 = normal hız, 2.0 = 2x hız, 0.5 = yarı hız
        """
        self.csv_source = csv_source
        self.replay_speed = replay_speed
        self._start_time = None
        self._base_timestamp = None
        self._active = True
    
    def get_name(self) -> str:
        return "REPLAY"
    
    def is_active(self) -> bool:
        return self._active and self.csv_source.is_active()
    
    def get_flows(self) -> Iterator[FlowData]:
        """CSV'den flow'ları zamanlayarak canlı gibi gönder"""
        self._start_time = time.time()
        self._base_timestamp = None
        
        for flow in self.csv_source.get_flows():
            if not self._active:
                break
            
            # İlk flow'un timestamp'ini base olarak al
            if self._base_timestamp is None:
                self._base_timestamp = flow.timestamp
            
            # Zamanlama hesapla
            elapsed_in_data = flow.timestamp - self._base_timestamp
            target_elapsed = elapsed_in_data / self.replay_speed
            
            # Bekleme süresi
            current_time = time.time()
            wait_until = self._start_time + target_elapsed
            wait_time = wait_until - current_time
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            # Timestamp'i güncelle
            flow.timestamp = time.time()
            yield flow
    
    def stop(self):
        self._active = False
