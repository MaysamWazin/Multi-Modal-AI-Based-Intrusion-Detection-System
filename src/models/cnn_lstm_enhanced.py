"""
Enhanced CNN-LSTM Model for Intelligent IDS
Geliştirilmiş mimari ile zaman serisi analizi için derin öğrenme modeli.
"""

from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    Conv1D, LSTM, Dense, Dropout, BatchNormalization,
    Input, GlobalMaxPooling1D, concatenate
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import numpy as np


def build_cnn_lstm_enhanced(input_shape, num_classes: int = 1):
    """
    Geliştirilmiş CNN-LSTM mimarisi
    
    Args:
        input_shape: (time_steps, num_features) tuple
        num_classes: Çıkış sınıf sayısı (1 = binary, >1 = multi-class)
    
    Returns:
        Compiled Keras model
    """
    time_steps, num_features = input_shape
    
    # Input layer
    inputs = Input(shape=input_shape, name='input_layer')
    
    # CNN Branch - Özellik çıkarımı
    # İlk CNN katmanı - küçük kernel ile lokal pattern'leri yakala
    conv1 = Conv1D(
        filters=64,
        kernel_size=3,
        activation='relu',
        padding='same',
        name='conv1d_1'
    )(inputs)
    conv1 = BatchNormalization(name='bn_1')(conv1)
    conv1 = Dropout(0.2, name='dropout_1')(conv1)
    
    # İkinci CNN katmanı - daha büyük kernel ile geniş pattern'leri yakala
    conv2 = Conv1D(
        filters=128,
        kernel_size=5,
        activation='relu',
        padding='same',
        name='conv1d_2'
    )(conv1)
    conv2 = BatchNormalization(name='bn_2')(conv2)
    conv2 = Dropout(0.3, name='dropout_2')(conv2)
    
    # Üçüncü CNN katmanı - daha derin özellikler
    conv3 = Conv1D(
        filters=128,
        kernel_size=3,
        activation='relu',
        padding='same',
        name='conv1d_3'
    )(conv2)
    conv3 = BatchNormalization(name='bn_3')(conv3)
    
    # Global pooling - zaman boyutunu azalt
    pooled = GlobalMaxPooling1D(name='global_max_pool')(conv3)
    
    # LSTM Branch - Zaman serisi bağımlılıkları
    # Bidirectional LSTM için önce reshape
    lstm_input = conv3  # CNN çıktısını LSTM'e ver
    
    # LSTM katmanları - zaman serisi pattern'lerini öğren
    lstm1 = LSTM(
        units=128,
        return_sequences=True,
        dropout=0.3,
        recurrent_dropout=0.3,
        name='lstm_1'
    )(lstm_input)
    
    lstm2 = LSTM(
        units=64,
        return_sequences=False,
        dropout=0.3,
        recurrent_dropout=0.3,
        name='lstm_2'
    )(lstm1)
    
    # Feature fusion - CNN ve LSTM çıktılarını birleştir
    if time_steps > 1:
        # Eğer sequence varsa, LSTM çıktısını kullan
        fused = concatenate([pooled, lstm2], name='feature_fusion')
    else:
        # Tek zaman adımı varsa sadece CNN çıktısını kullan
        fused = pooled
    
    # Dense layers - final classification
    dense1 = Dense(128, activation='relu', name='dense_1')(fused)
    dense1 = BatchNormalization(name='bn_dense_1')(dense1)
    dense1 = Dropout(0.4, name='dropout_dense_1')(dense1)
    
    dense2 = Dense(64, activation='relu', name='dense_2')(dense1)
    dense2 = Dropout(0.3, name='dropout_dense_2')(dense2)
    
    # Output layer
    if num_classes == 1:
        # Binary classification
        outputs = Dense(1, activation='sigmoid', name='output')(dense2)
        loss = 'binary_crossentropy'
        metrics = ['accuracy', 'precision', 'recall']
    else:
        # Multi-class classification
        outputs = Dense(num_classes, activation='softmax', name='output')(dense2)
        loss = 'sparse_categorical_crossentropy'
        metrics = ['accuracy']
    
    # Model oluştur
    model = Model(inputs=inputs, outputs=outputs, name='Enhanced_CNN_LSTM_IDS')
    
    # Compile
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss=loss,
        metrics=metrics
    )
    
    return model


def build_cnn_lstm_simple(input_shape, num_classes: int = 1):
    """
    Basit CNN-LSTM mimarisi (geriye uyumluluk için)
    """
    time_steps, num_features = input_shape
    
    model = Sequential(name='Simple_CNN_LSTM_IDS')
    
    # CNN layers
    model.add(Conv1D(
        filters=32,
        kernel_size=1,
        activation='relu',
        input_shape=input_shape,
        name='conv1d_1'
    ))
    
    model.add(Conv1D(
        filters=64,
        kernel_size=1,
        activation='relu',
        name='conv1d_2'
    ))
    
    # LSTM layer
    model.add(LSTM(
        64,
        return_sequences=False,
        dropout=0.3,
        name='lstm_1'
    ))
    
    model.add(Dropout(0.3, name='dropout_1'))
    
    # Dense layers
    model.add(Dense(64, activation='relu', name='dense_1'))
    model.add(Dense(32, activation='relu', name='dense_2'))
    
    # Output
    if num_classes == 1:
        model.add(Dense(1, activation='sigmoid', name='output'))
        loss = 'binary_crossentropy'
        metrics = ['accuracy']
    else:
        model.add(Dense(num_classes, activation='softmax', name='output'))
        loss = 'sparse_categorical_crossentropy'
        metrics = ['accuracy']
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss=loss,
        metrics=metrics
    )
    
    return model


def get_callbacks(model_path: str = "ids_cnn_lstm_enhanced.h5", patience: int = 5):
    """
    Training callbacks
    """
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
    ]
    return callbacks
