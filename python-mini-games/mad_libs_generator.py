import random

def mad_libs():
    nouns = ["cat", "dog", "house", "tree", "car", "computer", "phone"]
    verbs = ["ran", "jumped", "ate", "slept", "played", "sang", "danced"]
    adjectives = ["happy", "sad", "big", "small", "funny", "scary", "loud"]
    adverbs = ["quickly", "slowly", "loudly", "quietly", "happily", "sadly", "angrily"]

    noun1 = random.choice(nouns)
    verb1 = random.choice(verbs)
    adjective1 = random.choice(adjectives)
    adverb1 = random.choice(adverbs)
    noun2 = random.choice(nouns)


    story = f"The {adjective1} {noun1} {verb1} {adverb1} to the {noun2}."

    print(story)

if __name__ == "__main__":
    mad_libs()
