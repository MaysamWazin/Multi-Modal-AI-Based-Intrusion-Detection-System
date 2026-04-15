from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dropout, Dense


def build_cnn_lstm(input_shape):
    """
    input_shape = (time_steps, num_features)
    Bu projede time_steps = 1 olacak, num_features = 44.
    """
    model = Sequential()
    model.add(Conv1D(filters=32, kernel_size=1, activation="relu", input_shape=input_shape))
    model.add(Conv1D(filters=64, kernel_size=1, activation="relu"))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))  # binary classification için

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model
