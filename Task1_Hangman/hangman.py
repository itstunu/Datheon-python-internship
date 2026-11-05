# hangman.py
"""
Hangman - Datheon Python Internship, Task 1
===========================================

A terminal Hangman game with a 6-attempt limit and an ASCII gallows that
grows with every wrong guess.

Features
--------
* Secret word chosen with random.choice() from words.txt (next to this
  script). A small built-in list is used if the file is missing/empty.
* Repeated guesses trigger a warning and are NOT penalised.
* Input validation: exactly one alphabetic character is accepted.
* Graceful handling of Ctrl+C and EOF (Ctrl+D / Ctrl+Z).

Usage
----
    python hangman.py
"""

import random
from pathlib import Path

MAX_WRONG = 6                                    # attempts before losing
WORDS_FILE = Path(__file__).parent / "words.txt"  # never depends on cwd
SEPARATOR = "=" * 50

# Used only when words.txt is missing, unreadable or empty.
FALLBACK_WORDS = [
    "python", "github", "keyboard", "internship",
    "developer", "function", "variable", "terminal",
]

# 7 gallows stages: index 0 = empty gallows, index 6 = complete hangman.
# Each wrong guess adds: head, body, left arm, right arm, left leg, right leg.
# (Raw strings so the backslashes in the drawings are kept literally.)
STAGES = [
    # 0 - empty gallows
    r"""
  +---+
  |   |
      |
      |
      |
      |
=========
""",
    # 1 - head
    r"""
  +---+
  |   |
  O   |
      |
      |
      |
=========
""",
    # 2 - body
    r"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
""",
    # 3 - left arm
    r"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
""",
    # 4 - right arm
    r"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========
""",
    # 5 - left leg
    r"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========
""",
    # 6 - right leg (full hangman)
    r"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
""",
]


def load_words(path=WORDS_FILE):
    """Return a list of valid lowercase words from *path*.

    Falls back to FALLBACK_WORDS when the file is missing, unreadable,
    or contains no usable words.
    """
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        print("⚠ words.txt not found or unreadable - using built-in word list.")
        return FALLBACK_WORDS

    # Keep only plain a-z words (ignores blank lines / stray characters).
    words = [w.strip().lower() for w in lines]
    words = [w for w in words if w.isascii() and w.isalpha()]
    if not words:
        print("⚠ words.txt has no valid words - using built-in word list.")
        return FALLBACK_WORDS
    return words


def mask_word(word, guessed):
    """Return the word with unguessed letters hidden, e.g. 'P _ T H _ N'."""
    return " ".join(ch.upper() if ch in guessed else "_" for ch in word)


def read_guess(guessed):
    """Prompt until the user enters a valid, not-yet-guessed single letter.

    EOFError / KeyboardInterrupt are deliberately NOT caught here; main()
    handles them so the whole game can exit cleanly.
    """
    while True:
        raw = input("Guess a letter: ").strip().lower()
        if not raw:
            print("❌ Empty input - please type a letter.")
        elif len(raw) != 1:
            print("❌ Please enter exactly ONE letter at a time.")
        elif not (raw.isascii() and raw.isalpha()):
            print("❌ Letters A-Z only - no digits or symbols.")
        elif raw in guessed:
            # Duplicate guess: warn, but do not cost the player an attempt.
            print(f"⚠ You already guessed '{raw.upper()}'. No penalty - try another.")
        else:
            return raw


def show_status(word, guessed, wrong):
    """Print the gallows, masked word, wrong letters and attempts left."""
    wrong_letters = sorted(g for g in guessed if g not in word)
    print(SEPARATOR)
    print(STAGES[wrong].strip("\n"))
    print()
    print(f"Word:          {mask_word(word, guessed)}")
    print(f"Wrong letters: {', '.join(l.upper() for l in wrong_letters) or '-'}")
    print(f"Attempts left: {MAX_WRONG - wrong}")
    print(SEPARATOR)


def play_round(word):
    """Play one game with *word*. Return True on a win, False on a loss."""
    guessed = set()            # every letter tried so far (right or wrong)
    wrong = 0
    needed = set(word)         # unique letters that must be found

    # Loop ends on WIN (all letters found) or LOSE (wrong == MAX_WRONG).
    while wrong < MAX_WRONG and not needed <= guessed:
        show_status(word, guessed, wrong)
        letter = read_guess(guessed)
        guessed.add(letter)
        if letter in word:
            print(f"✔ Nice! '{letter.upper()}' is in the word.")
        else:
            wrong += 1
            print(f"❌ Sorry, '{letter.upper()}' is not in the word.")

    show_status(word, guessed, wrong)
    print(f"The word was: {word.upper()}")
    if wrong < MAX_WRONG:
        print("🎉 YOU WIN!")
        return True
    print("💀 GAME OVER")
    return False


def ask_play_again():
    """Ask 'Play again? (y/n)' until a valid answer is given."""
    while True:
        answer = input("Play again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("❌ Please answer 'y' or 'n'.")


def main():
    print(SEPARATOR)
    print("🎮  HANGMAN  -  Datheon Python Internship")
    print(SEPARATOR)
    print(f"Guess the word one letter at a time. {MAX_WRONG} wrong guesses and you lose!")

    words = load_words()
    try:
        while True:
            play_round(random.choice(words))
            if not ask_play_again():
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\n⚠ Game interrupted.")
    print("👋 Thanks for playing!")


if __name__ == "__main__":
    main()
