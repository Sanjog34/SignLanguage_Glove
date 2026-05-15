from gtts import gTTS
import os
import time

# Folders
CONSONANT_DIR = "../sounds/consonants_mp3"
WORD_DIR = "../sounds/words_mp3"
NUMBERS_DIR = "../sounds/numbers_mp3"

# Create folders if not exist
os.makedirs(CONSONANT_DIR, exist_ok=True)
os.makedirs(WORD_DIR, exist_ok=True)
os.makedirs(NUMBERS_DIR, exist_ok=True)

consonants = [
    "क", "ख", "ग", "घ", "ङ",
    "च", "छ", "ज", "झ", "ञ",
    "ट", "ठ", "ड", "ढ", "ण",
    "त", "थ", "द", "ध", "न",
    "प", "फ", "ब", "भ", "म",
    "य", "र", "ल", "व",
    "श", "ष", "स", "ह",
    "क्ष", "त्र", "ज्ञ"
]

words = [
    # ("mero", "मेरो"),
    # ("timi", "तिमी"),
    # ("khana", "खाना"),
    # ("pani", "पानी"),
    # ("namaste", "नमस्ते"),
    # ("dhanyabad", "धन्यवाद"),
    # ("sanchai", "सन्चै"),
    ("aaja", "आ ज"),
    # ("kati", "कति"),
    # ("sathi", "साथी"),
    # ("fist", "मुट्ठी"),
    # ("thumbup", "राम्रो"),
    # ("twoo", "दुईई"),
    # ("day","बार"),
    # ("chinnu","चिन्नु")
    ("malai","मलाई"),
    ("ramro","राम्रो"),
    ("naam", "नाम"),
    ("ho", "हो"),
    ("huncha", "हुन्छअ"),
    ("mero", "मेरो")
]

nepali_numbers = [
    "०","१","२","३","४","५","६","७","८","९"
]

print("\nGenerating Nepali TTS files...\n")

# === Generate consonants (1.mp3, 2.mp3, ...) ===
# for i, consonant in enumerate(consonants, start=1):
#     filename = f"{CONSONANT_DIR}/{i}.mp3"
#     print(f"Saving consonant: {consonant} -> {filename}")

#     if not os.path.exists(filename):
#         tts = gTTS(text=consonant, lang='hi')
#         tts.save(filename)

#     # play
#     os.system(f"mpg123 '{filename}' > /dev/null 2>&1")
#     time.sleep(0.5)

# === Generate words (1.mp3, 2.mp3, ...) ===
for  roman,dev in words:
    filename = f"{WORD_DIR}/{roman}.mp3"
    print(f"Saving word: {dev} -> {filename}")

    if not os.path.exists(filename):
        tts = gTTS(text=dev, lang='hi')
        tts.save(filename)

    # play
        os.system(f"mpg123 '{filename}' > /dev/null 2>&1")
        time.sleep(0.5)
    
# === Generate numbers (0.mp3, 1.mp3, ...) ===
# for i, number in enumerate(nepali_numbers, start=0):
#     filename = f"{NUMBERS_DIR}/{i}.mp3"
#     print(f"Saving number: {number} -> {filename}")

#     if not os.path.exists(filename):
#         tts = gTTS(text=number, lang='hi')
#         tts.save(filename)

#     # play
#     os.system(f"mpg123 '{filename}' > /dev/null 2>&1")
#     time.sleep(0.5)

print("\n All audio files generated and played successfully!\n")
