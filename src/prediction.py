import serial
import joblib
import pandas as pd
import dictate

PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
MODEL_FILE = 'my_model_newSensorData_alpha.joblib'  # path to the trained model

# Load trained model
model = joblib.load(MODEL_FILE)

# Open serial
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
print(f" Serial connected on {PORT}. Receiving data...\n")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or ',' not in line:
            continue

        parts = line.split(',')
        if len(parts) != 8:
            continue

        try:
            idxUp,idxLow,midUp,midLow,ringUp,ringLow,thumb,pinky = map(float, parts)
        except ValueError:
            continue

        # Predict
        X_input = pd.DataFrame([[idxUp,idxLow,midUp,midLow,ringUp,ringLow,thumb,pinky]], columns=['idxUp','idxLow','midUp','midLow','ringUp','ringLow','thumb','pinky'])
        pred = model.predict(X_input)[0]
        if pred == 2:
            label = 'ga'
            dictate.play_sound(dictate.CONSONANT_DIR + '/3.mp3')
        elif pred == 0:
            label = 'ka'
            dictate.play_sound(dictate.CONSONANT_DIR + '/1.mp3')
        elif pred == 1:
            label = 'kha'
            dictate.play_sound(dictate.CONSONANT_DIR + '/2.mp3')
        elif pred == 3:
            label = 'gha'
            dictate.play_sound(dictate.CONSONANT_DIR + '/4.mp3')
        elif pred == 4:
            label = 'ek'
            dictate.play_sound(dictate.NUMBERS_DIR + '/1.mp3')
        elif pred == 5:
            label = 'dui'
            dictate.play_sound(dictate.NUMBERS_DIR + '/2.mp3')
        elif pred == 6:
            label = 'tin'
            dictate.play_sound(dictate.NUMBERS_DIR + '/3.mp3')
        print(f"Label: {label}")

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    ser.close()
