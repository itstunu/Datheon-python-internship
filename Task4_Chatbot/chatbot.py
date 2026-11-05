# chatbot.py
"""
Rule-Based Support Chatbot - Datheon Python Internship, Task 4
=============================================================

A customer-support bot that understands questions through regular
expressions. All intents, patterns and replies live in sample_faq.json, so
the bot can be extended without touching any Python code.

How matching works
------------------
1. The user's text is normalised (lowercase, trimmed, single spaces).
2. Every pattern of every intent is searched with  \\b(?:pattern)\\b .
3. If several patterns match, the one matching the LONGEST piece of text
   wins (ties are broken by the longer pattern) - so specific questions
   beat generic words like "hi".
4. No match -> a random fallback reply.

Usage
-----
    python chatbot.py
    (type bye / exit / quit / goodbye to leave)
"""

import json
import random
import re
from pathlib import Path

FAQ_FILE = Path(__file__).parent / "sample_faq.json"
SEPARATOR = "=" * 50
EXIT_WORDS = {"bye", "exit", "quit", "goodbye"}

FALLBACK_RESPONSES = [
    "Sorry, I didn't quite get that. Could you rephrase your question?",
    "Hmm, I'm not sure about that one. Try asking about shipping, returns, payment, warranty or opening hours.",
    "I don't have an answer for that yet. You can reach a human at support@datheonshop.example.",
]
ALREADY_GREETED_RESPONSES = [
    "We've already said hello 😊 - what can I help you with?",
    "Hi again! Ask me anything about orders, shipping or returns.",
]
FAREWELL_RESPONSES = [
    "Goodbye! 👋 Thanks for chatting with us.",
    "Bye! Have a wonderful day!",
]

# Tiny built-in FAQ so the bot still works if sample_faq.json is missing/broken.
DEFAULT_FAQ = {
    "greeting": {
        "patterns": ["hi", "hello", "hey"],
        "responses": ["Hello! How can I help you today?", "Hi there! What can I do for you?"],
    },
    "thanks": {
        "patterns": ["thanks?", "thank you"],
        "responses": ["You're welcome!", "Happy to help!"],
    },
}


def load_faq(path=FAQ_FILE):
    """Load intents from JSON; fall back to DEFAULT_FAQ on any problem."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"⚠ {Path(path).name} not found - using a minimal built-in FAQ.")
        return DEFAULT_FAQ
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"⚠ Could not read {Path(path).name} ({exc}) - using a minimal built-in FAQ.")
        return DEFAULT_FAQ

    if not isinstance(data, dict) or not data:
        print("⚠ FAQ file has an unexpected structure - using a minimal built-in FAQ.")
        return DEFAULT_FAQ
    return data


def normalize(text):
    """Lowercase, strip and collapse repeated whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def match_intent(text, faq):
    """Return the best-matching intent name for *text*, or None.

    Each pattern is searched as  \\b(?:pattern)\\b . The non-capturing group
    makes alternations such as "hi|hello" respect the word boundaries.
    The match covering the most characters wins (longest match).
    """
    best_intent = None
    best_score = (0, 0)  # (matched text length, pattern length)
    for intent, block in faq.items():
        patterns = block.get("patterns", []) if isinstance(block, dict) else []
        for pattern in patterns:
            try:
                found = re.search(rf"\b(?:{pattern})\b", text)
            except (re.error, TypeError):
                continue  # ignore a broken regex instead of crashing
            if found:
                score = (len(found.group(0)), len(pattern))
                if score > best_score:
                    best_intent, best_score = intent, score
    return best_intent


def get_response(intent, faq):
    """Pick a random reply for *intent*; use fallback if none is defined."""
    block = faq.get(intent, {}) if intent else {}
    responses = block.get("responses") if isinstance(block, dict) else None
    if isinstance(responses, list) and responses:
        return random.choice(responses)
    return random.choice(FALLBACK_RESPONSES)


def main():
    faq = load_faq()
    greeted = False  # "hi" only triggers the full greeting once

    print(SEPARATOR)
    print("🤖  SUPPORT CHATBOT  -  Datheon Internship")
    print(SEPARATOR)
    print("Ask me about shipping, returns, payment, warranty, hours or contact.")
    print("Type 'bye' to exit.\n")

    try:
        while True:
            raw = input("You: ")
            text = normalize(raw)

            if not text:
                print("Bot: Please type a question and I'll do my best to help.\n")
                continue

            # Strip trailing punctuation so "Bye!" counts as an exit word.
            if text.strip(" .!?,") in EXIT_WORDS:
                print(f"Bot: {random.choice(FAREWELL_RESPONSES)}")
                break

            intent = match_intent(text, faq)
            if intent == "greeting":
                if greeted:
                    reply = random.choice(ALREADY_GREETED_RESPONSES)
                else:
                    reply = get_response(intent, faq)
                    greeted = True
            elif intent:
                reply = get_response(intent, faq)
            else:
                reply = random.choice(FALLBACK_RESPONSES)
            print(f"Bot: {reply}\n")
    except (KeyboardInterrupt, EOFError):
        print(f"\nBot: {random.choice(FAREWELL_RESPONSES)}")


if __name__ == "__main__":
    main()
