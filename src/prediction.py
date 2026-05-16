import serial
import joblib
import pandas as pd
import dictate_01
import dictate

PORT = '/dev/ttyUSB1'
BAUD_RATE = 115200
MODEL_FILE = '../models(joblib)/Gesture_Model_20K_04.joblib'

model = joblib.load(MODEL_FILE)

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
ser.reset_input_buffer()
ser.reset_output_buffer()

print(f"Serial connected on {PORT}. Receiving data...\n")

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            continue

        # DEBUG (remove later)
        # print("RAW:", line)

        if ',' not in line:
            continue

        parts = line.split(',')
        if len(parts) < 17:
            continue

        parts = parts[:11]

        try:
            idxUp, idxLow, midUp, midLow, ringUp, ringLow, thumb, pinky, ax, ay, az = map(float, parts)
        except ValueError:
            continue

        X_input = pd.DataFrame([[
            idxUp, idxLow, midUp, midLow,
            ringUp, ringLow, thumb, pinky,
            ax, ay, az
        ]], columns=[
            'idxUp','idxLow','midUp','midLow',
            'ringUp','ringLow','thumb','pinky',
            'ax','ay','az'
        ])

        pred = model.predict(X_input)[0]

        if pred == 0:
            label = 'ka'
            dictate_01.play_sound(dictate.CONSONANT_DIR + '/0.mp3',1)
        elif pred == 1:
            label = 'kha'
            dictate_01.play_sound(dictate.CONSONANT_DIR + '/1.mp3',1)
        elif pred == 2:
            label = 'ga'
            dictate_01.play_sound(dictate.CONSONANT_DIR + '/2.mp3',1)
        elif pred == 3:
            label = 'gha'
            dictate_01.play_sound(dictate.CONSONANT_DIR + '/3.mp3',1)
        elif pred == 4:
            label = 'nga'
            dictate_01.play_sound(dictate.CONSONANT_DIR + '/4.mp3',1)
        elif pred == 44:
            label = 'cha'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/5.mp3',1)
        elif pred == 5:
            label = 'ek'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/1.mp3',1)
        elif pred == 6:
            label = 'dui'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/2.mp3',1)
        elif pred == 7:
            label = 'tin'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/3.mp3',1)
        elif pred == 8:
            label = 'char'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/4.mp3',1)
        elif pred == 10:
            label = 'pach'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/5.mp3',1)
        elif pred == 11:
            label = 'chha'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/6.mp3',1)
        elif pred == 12:
            label = 'saat'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/7.mp3',1)
        elif pred == 13:
            label = 'aath'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/8.mp3',1)
        elif pred == 14:
            label = 'naau'
            dictate_01.play_sound(dictate.NUMBERS_DIR + '/9.mp3',1)
        
        
        
        else:
            label = 'unknown'

        print(f"Label: {label}")

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    ser.close()