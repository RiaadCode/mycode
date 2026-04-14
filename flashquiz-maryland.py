#!/usr/bin/env python3
# flashquiz-maryland.py
# A beginner-friendly Flash Card Quiz about Maryland!
# Run this script from your terminal: python3 flashquiz-maryland.py
#
# Changes in this version:
# - Robust JSON loader with helpful errors and validation.
# - Backwards-compatible support for "answer" and "answers" fields (normalizes to "answers").
# - normalize_answer() and tolerant matching using difflib for small typos.
# - CLI flags: --shuffle, --count, --seed, --file
# - Simple, beginner-friendly code.

import argparse
import json
import os
import random
import re
import sys
import difflib

# --- Helpers: normalization and matching ---


def normalize_answer(text):
    """Normalize text for comparison:
    - None -> ''
    - lowercased
    - strip surrounding whitespace
    - remove most punctuation (keep internal hyphens/apostrophes and digits)
    - collapse multiple spaces
    """
    if text is None:
        return ""
    text = str(text).lower().strip()
    # Remove punctuation except letters, digits, whitespace, hyphen, apostrophe
    text = re.sub(r"[^\w\s'-]", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def digits_only(text):
    """Return only digit characters from text (useful for numeric answers)."""
    return re.sub(r"\D", "", text or "")


def is_match(user_input, accepted_answers, cutoff=0.82):
    """Return True if user_input matches any of accepted_answers.
    Matching strategy:
    1. If accepted answer looks numeric (all digits), compare digits-only equality.
    2. Exact normalized equality.
    3. Fuzzy match using difflib.SequenceMatcher ratio >= cutoff.
    """
    user_raw = user_input or ""
    user_norm = normalize_answer(user_raw)

    for a in accepted_answers:
        a_norm = normalize_answer(a)

        # Numeric answer special-case: if the accepted answer contains at least one digit
        a_digits = digits_only(a_norm)
        if a_digits and digits_only(user_norm) == a_digits:
            return True

        # Exact normalized match
        if user_norm == a_norm:
            return True

        # Fuzzy match (use ratio)
        ratio = difflib.SequenceMatcher(None, user_norm, a_norm).ratio()
        if ratio >= cutoff:
            return True

    return False


# --- Load Questions ---


def load_questions(filename):
    """Load flash card questions from a JSON file with helpful errors and validation.

    Returns a list of normalized cards where each card has:
      - 'question' (string)
      - 'answers' (list of strings)

    If the file contains malformed JSON, show a friendly message and exit.
    If individual cards are invalid, skip them with a warning.
    """
    if not os.path.exists(filename):
        print(f"Error: Could not find '{filename}'. Make sure it is in the same folder.")
        sys.exit(1)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {filename}: {e}")
        print("Hint: Check for trailing commas, missing quotes, or use a JSON linter.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: could not read {filename}: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: expected a JSON array of cards in {filename}.")
        sys.exit(1)

    normalized = []
    for idx, card in enumerate(data):
        if not isinstance(card, dict):
            print(f"Warning: skipping card at index {idx} (not an object).")
            continue

        question = card.get("question")
        answers_field = card.get("answers")
        single_answer = card.get("answer")

        if not question or not (answers_field or single_answer):
            print(f"Warning: skipping invalid card at index {idx} (missing question or answer).")
            continue

        # Normalize to 'answers' list (backwards-compatible)
        if isinstance(answers_field, list):
            answers = [str(a).strip() for a in answers_field if a is not None]
        elif isinstance(single_answer, (str, int, float)):
            answers = [str(single_answer).strip()]
        else:
            # Unexpected format
            print(f"Warning: skipping card at index {idx} (invalid 'answers' format).")
            continue

        # Remove empty answers
        answers = [a for a in answers if a != ""]

        if not answers:
            print(f"Warning: skipping card at index {idx} (no valid answers after normalization).")
            continue

        normalized.append({"question": str(question).strip(), "answers": answers})

    if not normalized:
        print(f"Error: no valid cards found in {filename}.")
        sys.exit(1)

    return normalized


# --- Run the Quiz ---


def run_quiz(questions, shuffle=False, count=None, seed=None):
    """Ask each question, check the answer, and track the score."""
    if seed is not None:
        random.seed(seed)

    cards = list(questions)  # copy
    total_available = len(cards)

    if shuffle:
        random.shuffle(cards)

    if count is not None:
        try:
            n = int(count)
            if n < 1:
                print("Invalid --count value; must be >= 1. Using all questions.")
            else:
                cards = cards[:min(n, len(cards))]
        except ValueError:
            print("Invalid --count value; using all questions.")

    score = 0
    total = len(cards)
    missed = []  # store tuples (index, card, user_answer)

    print("\n🦀  Welcome to the Maryland Flash Card Quiz!  🦀")
    print("=" * 60)
    print("Type your answer and press Enter.")
    print("Answers are not case-sensitive and small typos are accepted.")
    print("You can run with --shuffle and --count to control the session.")
    print("=" * 60 + "\n")

    for i, card in enumerate(cards, start=1):
        question = card["question"]
        accepted = card["answers"]
        display_answer = accepted[0]  # first answer as canonical display

        print(f"Question {i}/{total}:")
        print(f"  {question}")
        user_answer = input("  Your answer: ").strip()

        if is_match(user_answer, accepted):
            print("  ✅ Correct!\n")
            score += 1
        else:
            print(f"  ❌ Not quite. The answer is: {display_answer}\n")
            missed.append((i, card, user_answer))

    return score, total, missed, total_available


# --- Show Final Score ---


def show_score(score, total, missed, total_available):
    """Display the final score with a simple review of missed questions."""
    print("=" * 60)
    print(f"Quiz complete! You got {score} out of {total} correct.")
    percentage = (score / total) * 100 if total else 0.0
    print(f"Score: {percentage:.1f}% ({score}/{total})")
    if percentage == 100:
        print("🌟 Perfect score! You really know Maryland!")
    elif percentage >= 70:
        print("👍 Great job! You know your Maryland facts!")
    elif percentage >= 40:
        print("📚 Not bad! Keep exploring Maryland to learn more.")
    else:
        print("🦀 Keep at it! Maryland has a lot of cool history to discover.")

    if missed:
        print("\nQuestions to review:")
        for i, card, user in missed[:10]:
            print(f"  Q{i}: {card['question']}")
            print(f"    Correct: {card['answers'][0]}")
            if len(card["answers"]) > 1:
                # show a couple of alternative acceptable forms
                extras = card["answers"][1:3]
                print(f"    Also accepted: {', '.join(extras)}")
            print(f"    Your answer: {user}")
    else:
        print("\nNo missed questions — well done!")

    if total_available > total:
        print(f"\nNote: You practiced {total} questions this session out of {total_available} available.")
    print("=" * 60)


# --- Main Entry Point ---


def main():
    parser = argparse.ArgumentParser(description="Maryland Flash Card Quiz")
    parser.add_argument(
        "--file",
        "-f",
        default=os.path.join(os.path.dirname(__file__), "questions.json"),
        help="Path to questions JSON file (default: questions.json in this folder)",
    )
    parser.add_argument("--shuffle", action="store_true", help="Shuffle questions before running")
    parser.add_argument("--count", type=int, help="Limit number of questions in this session")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible shuffles")
    args = parser.parse_args()

    questions = load_questions(args.file)
    score, total, missed, total_available = run_quiz(questions, shuffle=args.shuffle, count=args.count, seed=args.seed)
    show_score(score, total, missed, total_available)


if __name__ == "__main__":
    main()
