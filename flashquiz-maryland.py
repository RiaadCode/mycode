# flashquiz-maryland.py
# A beginner-friendly Flash Card Quiz about Maryland!
# Run this script from your terminal: python3 flashquiz-maryland.py

import json  # Used to load questions from the JSON file
import os    # Used to check that the questions file exists

# --- Load Questions ---

def load_questions(filename):
    """Load flash card questions from a JSON file."""
    if not os.path.exists(filename):
        print(f"Error: Could not find '{filename}'. Make sure it is in the same folder.")
        exit(1)

    with open(filename, "r") as f:
        questions = json.load(f)

    return questions


# --- Run the Quiz ---

def run_quiz(questions):
    """Ask each question, check the answer, and track the score."""
    score = 0                  # How many correct answers so far
    total = len(questions)     # Total number of questions

    print("\n🦀  Welcome to the Maryland Flash Card Quiz!  🦀")
    print("=" * 48)
    print("Type your answer and press Enter.")
    print("Answers are not case-sensitive.")
    print("=" * 48 + "\n")

    for i, card in enumerate(questions, start=1):
        question = card["question"]
        correct_answer = card["answer"].lower().strip()

        # Show the question number and the question
        print(f"Question {i} of {total}:")
        print(f"  {question}")

        # Get the user's answer
        user_answer = input("  Your answer: ").lower().strip()

        # Check if the answer is correct
        if user_answer == correct_answer:
            print("  ✅ Correct!\n")
            score += 1
        else:
            print(f"  ❌ Not quite. The answer is: {card['answer']}\n")

    return score, total


# --- Show Final Score ---

def show_score(score, total):
    """Display the final score with a fun message."""
    print("=" * 48)
    print(f"Quiz complete! You got {score} out of {total} correct.")

    # Give a fun message based on how well the user did
    percentage = (score / total) * 100

    if percentage == 100:
        print("🌟 Perfect score! You really know Maryland!")
    elif percentage >= 70:
        print("👍 Great job! You know your Maryland facts!")
    elif percentage >= 40:
        print("📚 Not bad! Keep exploring Maryland to learn more.")
    else:
        print("🦀 Keep at it! Maryland has a lot of cool history to discover.")

    print("=" * 48)


# --- Main Entry Point ---

if __name__ == "__main__":
    # The questions file should be in the same folder as this script
    questions_file = os.path.join(os.path.dirname(__file__), "questions.json")

    questions = load_questions(questions_file)
    score, total = run_quiz(questions)
    show_score(score, total)
