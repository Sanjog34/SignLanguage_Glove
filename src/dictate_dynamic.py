import os

# Directories
CONSONANT_DIR = "../sounds/consonants_mp3"
WORD_DIR = "../sounds/words_mp3"
NUMBERS_DIR = "../sounds/numbers_mp3"


def play_sound(file_path):
    if not hasattr(play_sound, "last_file"):
        play_sound.last_file = None
    if not hasattr(play_sound, "counter"):
        play_sound.counter = 0

    # If filename changed, reset counter
    if play_sound.last_file != file_path:
        play_sound.last_file = file_path
        play_sound.counter = 1
    else:
        play_sound.counter += 1

    # Play only when same file appears 10 times
    if play_sound.counter == 1:
        if os.path.exists(file_path):
            os.system(f"mpg123 '{file_path}' > /dev/null 2>&1")
        else:
            print(f"File not found: {file_path}")