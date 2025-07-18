import time
import random

def typing_speed_test():
    words = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]
    test_words = random.sample(words, 5)
    sentence = " ".join(test_words)

    print("Type the following sentence:")
    print(sentence)
    input("Press Enter to start...")

    start_time = time.time()
    typed_sentence = input()
    end_time = time.time()

    if typed_sentence == sentence:
        elapsed_time = end_time - start_time
        words_per_minute = (len(sentence.split()) / elapsed_time) * 60
        print(f"Correct! Your typing speed is approximately {words_per_minute:.2f} words per minute.")
    else:
        print("Incorrect. Please try again.")

if __name__ == "__main__":
    typing_speed_test()
