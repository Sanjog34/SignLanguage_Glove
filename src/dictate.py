import os

# Directories
CONSONANT_DIR = "../sounds/consonants_mp3"
WORD_DIR = "../sounds/words_mp3"
NUMBERS_DIR = "../sounds/numbers_mp3"
TRAINED_SOUNDS_DIR="../sounds/trained_sounds"

def play_sound(file_path, static_playing: int) -> int:
    if not hasattr(play_sound, "last_file"):
        play_sound.last_file = None
    if not hasattr(play_sound, "counter"):
        play_sound.counter = 0

    # Track file changes and update counter regardless of static_playing
    if play_sound.last_file != file_path:
        play_sound.last_file = file_path
        play_sound.counter = 1
    else:
        play_sound.counter += 1

    # Only play if armed (not the first prediction after a dynamic gesture)
    print(" ditcate side  "+ str(play_sound.counter) + "  " + str(static_playing),end="")
    if play_sound.counter == 15 and static_playing:
        if os.path.exists(file_path):
            os.system(f"mpg123 '{file_path}' > /dev/null 2>&1")
            return 1
        else:
            print(f"File not found: {file_path}")
            return 0
    if play_sound.counter > 15 :
        changed=1
        print(" returning 1")
        return 1
    if changed==1 :
        print(" returning 1")
        return 1 
    else :
        return 0
    
    # Always return True to arm subsequent predictions
    

# Mapping for consonants -> 1.mp3, 2.mp3, ...
# consonant_map = {consonants[i]: f"{i+1}.mp3" for i in range(len(consonants))}
# # Mapping for words -> roman.mp3
# word_map = {nepali: roman + ".mp3" for roman, nepali in words}
# # Mapping for numbers -> 0.mp3, 1.mp3, ...
# number_map = {nepali_numbers[i]: f"{i}.mp3" for i in range(len(nepali_numbers))}

# print("Type 'exit' to quit.")

# while True:
#     user_input = input("Enter Nepali consonant, word, or number: ").strip()
    
#     if user_input.lower() == "exit":
#         break
    
#     if user_input in consonant_map:
#         play_sound(os.path.join(CONSONANT_DIR, consonant_map[user_input]))
#     elif user_input in word_map:
#         play_sound(os.path.join(WORD_DIR, word_map[user_input]))
#     elif user_input in number_map:
#         play_sound(os.path.join(NUMBERS_DIR, number_map[user_input]))
#     else:
#         print("Input not recognized.")
