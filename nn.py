import csv
from functools import cache
import os
import random
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras import Sequential, models, layers
import tensorflow as tf

MODEL_FILE = 'my_model.keras'
SCALER_FILE = 'scaler.pkl'


def trim_csv_random(input_file, max_rows, output_file="DEFAULT.csv"):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Read the header
        
        # Read all rows after the header
        rows = list(reader)
        
        # Randomly shuffle the rows
        random.shuffle(rows)
        
        # Keep only 'max_rows' rows
        trimmed_rows = rows[:max_rows]
        
    # Write the trimmed rows to the output file
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)  # Write the header
        writer.writerows(trimmed_rows)  # Write the trimmed rows
    
    # Delete the original input file
    os.remove(input_file)
    
    # Rename the output file to the original input file's name
    os.rename(output_file, input_file)

def load_and_preprocess_data(csv_file, maxSize = 250000):
    # Load the CSV file
    trim_csv_random(csv_file, maxSize)

    data = pd.read_csv(csv_file)

    # Split into input (X) and output (y)
    X = data.iloc[:, 1:-1].values  # All columns except the first and last
    y = data.iloc[:, -1].values    # The last column

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Normalize the data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, scaler

def build_model(input_dim):
    model = Sequential()
    model.add(layers.Dense(units=128, activation='relu', input_dim=input_dim))
    model.add(layers.Dense(units=64, activation='relu'))
    model.add(layers.Dense(units=32, activation='relu'))
    model.add(layers.Dense(units=16, activation='relu'))
    model.add(layers.Dense(units=1, activation='linear'))  # Linear activation for regression
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_squared_error'])
    return model

@tf.function
def tf_predict(model, input_tensor):
    return model(input_tensor)

def predict(model, scaler, input_data):
    if model is not None and scaler is not None:
        input_vector = np.array(input_data).reshape(1, -1)
        input_vector = scaler.transform(input_vector)
        input_tensor = tf.convert_to_tensor(input_vector, dtype=tf.float32)
        prediction = tf_predict(model, input_tensor)
        return prediction.numpy()[0][0]
    return random.random()

def get_model_and_scaler(csv_file=None, retrain=False):
    model = None
    scaler = None
    if not os.path.exists(csv_file):
        return model, scaler
    if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE) and not retrain:
        # Load existing model and scaler
        model = models.load_model(MODEL_FILE)
        scaler = joblib.load(SCALER_FILE)
    elif csv_file:
        # Train a new model if CSV file is provided
        X_train, X_test, y_train, y_test, scaler = load_and_preprocess_data(csv_file)
        model = build_model(X_train.shape[1])
        model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))
        model.save(MODEL_FILE)
        joblib.dump(scaler, SCALER_FILE)
    
    return model, scaler

if __name__ == "__main__":
    # This part runs only if the script is executed directly
    csv_file = 'game_moves.csv'  # Replace with your actual CSV file
    model, scaler = get_model_and_scaler(csv_file, retrain=True)

    # Evaluate the model
    X_train, X_test, y_train, y_test, _ = load_and_preprocess_data(csv_file)
    loss, mse = model.evaluate(X_test, y_test)
    print(f'Loss: {loss}, Mean Squared Error: {mse}')

    # Get 10 random rows from the test set for output comparison
    random_indices = np.random.choice(X_test.shape[0], 10, replace=False)
    random_X = X_test[random_indices]
    random_y = y_test[random_indices]

    # Print actual vs predicted outputs
    print("Actual vs Predicted outputs:")
    for i in range(10):
        actual = random_y[i]
        predicted = predict(model, scaler, random_X[i])
        print(f"Actual: {actual}, Predicted: {predicted}")
