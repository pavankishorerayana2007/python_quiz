from flask import Flask, render_template, jsonify, request, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

QUIZ_DATA = {
    "Level 1 - Beginner": [
        {"question": "What is Python?", "options": {"A": "Programming Language", "B": "Operating System", "C": "Browser", "D": "Database"}, "answer": "A", "explanation": "Python is a high-level programming language."},
        {"question": "Which symbol is used for comments?", "options": {"A": "//", "B": "#", "C": "/*", "D": "@"}, "answer": "B", "explanation": "The # symbol is used for single-line comments in Python."},
        {"question": "Which function displays output?", "options": {"A": "input()", "B": "scan()", "C": "print()", "D": "display()"}, "answer": "C", "explanation": "The print() function displays output."},
        {"question": "Which data type stores whole numbers?", "options": {"A": "str", "B": "float", "C": "list", "D": "int"}, "answer": "D", "explanation": "The int data type stores integer values."},
        {"question": "What is the output of 5 + 5?", "options": {"A": "10", "B": "55", "C": "5", "D": "0"}, "answer": "A", "explanation": "The + operator adds two numbers."}
    ],
    "Level 2 - Intermediate": [
        {"question": "Which data structure stores multiple values?", "options": {"A": "int", "B": "list", "C": "float", "D": "bool"}, "answer": "B", "explanation": "A list stores multiple values in one variable."},
        {"question": "Which loop is used to iterate over a sequence?", "options": {"A": "if", "B": "def", "C": "for", "D": "return"}, "answer": "C", "explanation": "A for loop iterates over sequence elements."},
        {"question": "Which brackets are used for dictionaries?", "options": {"A": "[]", "B": "()", "C": "<>", "D": "{}"}, "answer": "D", "explanation": "Dictionaries use curly braces with key-value pairs."},
        {"question": "Which keyword checks a condition?", "options": {"A": "if", "B": "print", "C": "import", "D": "break"}, "answer": "A", "explanation": "The if keyword executes code based on a condition."},
        {"question": "What does len() return?", "options": {"A": "Data type", "B": "Length", "C": "Memory", "D": "Index"}, "answer": "B", "explanation": "len() returns the number of items in an object."}
    ],
    "Level 3 - Advanced": [
        {"question": "Which keyword defines a function?", "options": {"A": "function", "B": "fun", "C": "def", "D": "define"}, "answer": "C", "explanation": "The def keyword is used to define functions."},
        {"question": "Which keyword handles exceptions?", "options": {"A": "try", "B": "loop", "C": "check", "D": "error"}, "answer": "A", "explanation": "The try block is used with except to handle exceptions."},
        {"question": "What does append() do?", "options": {"A": "Removes an item", "B": "Adds an item at the end", "C": "Sorts a list", "D": "Clears a list"}, "answer": "B", "explanation": "append() adds a new element to the end of a list."},
        {"question": "Which keyword exits a loop?", "options": {"A": "continue", "B": "pass", "C": "return", "D": "break"}, "answer": "D", "explanation": "The break statement immediately terminates a loop."},
        {"question": "What does a dictionary store?", "options": {"A": "Only numbers", "B": "Only strings", "C": "Key-value pairs", "D": "Only lists"}, "answer": "C", "explanation": "A dictionary stores data as key-value pairs."}
    ]
}
LEVELS = list(QUIZ_DATA.keys())

@app.route("/")
def home():
    return render_template("index.html")

def current_question():
    level = session.get("level", 0)
    question_index = session.get("question", 0)
    if level >= len(LEVELS):
        return None
    return QUIZ_DATA[LEVELS[level]][question_index]

@app.post("/api/start")
def start_quiz():
    session["level"] = 0
    session["question"] = 0
    session["total_score"] = 0
    session["total_questions"] = sum(len(items) for items in QUIZ_DATA.values())
    session["level_score"] = 0
    session["answered"] = False
    return jsonify(question_payload())

def question_payload():
    level = session["level"]
    q_index = session["question"]
    q = current_question()
    return {
        "done": False,
        "level": level + 1,
        "level_name": LEVELS[level],
        "level_total": len(QUIZ_DATA[LEVELS[level]]),
        "question_number": q_index + 1,
        "total_levels": len(LEVELS),
        "question": q["question"],
        "options": q["options"],
        "total_score": session["total_score"]
    }

@app.get("/api/question")
def get_question():
    if "level" not in session:
        return jsonify({"error": "Start a quiz first."}), 400
    if session.get("level", 0) >= len(LEVELS):
        return jsonify({"done": True}), 200
    return jsonify(question_payload())

@app.post("/api/answer")
def answer():
    if "level" not in session:
        return jsonify({"error": "Start a quiz first."}), 400
    if session.get("answered"):
        return jsonify({"error": "This question has already been answered."}), 400
    data = request.get_json(silent=True) or {}
    choice = str(data.get("answer", "")).strip().upper()
    if choice not in ("A", "B", "C", "D"):
        return jsonify({"error": "Choose A, B, C or D."}), 400

    q = current_question()
    correct = choice == q["answer"]
    if correct:
        session["total_score"] += 1
        session["level_score"] += 1
    session["answered"] = True
    return jsonify({
        "correct": correct,
        "correct_answer": q["answer"],
        "explanation": q["explanation"],
        "level_score": session["level_score"],
        "total_score": session["total_score"]
    })

@app.post("/api/next")
def next_question():
    if "level" not in session or not session.get("answered"):
        return jsonify({"error": "Answer the current question first."}), 400

    level = session["level"]
    q_index = session["question"]
    level_name = LEVELS[level]
    level_finished = q_index == len(QUIZ_DATA[level_name]) - 1
    completed_level_score = session["level_score"] if level_finished else None

    if not level_finished:
        session["question"] = q_index + 1
        session["answered"] = False
        return jsonify({"level_finished": False, **question_payload()})

    session["level"] = level + 1
    session["question"] = 0
    session["level_score"] = 0
    session["answered"] = False

    if session["level"] >= len(LEVELS):
        total = session["total_score"]
        count = session["total_questions"]
        percentage = round((total / count) * 100, 2)
        performance = "Excellent!" if percentage >= 80 else "Good!" if percentage >= 60 else "Average!" if percentage >= 40 else "Needs Improvement!"
        return jsonify({
            "done": True,
            "level_finished": True,
            "completed_level": level_name,
            "completed_level_score": completed_level_score,
            "total_score": total,
            "total_questions": count,
            "wrong_answers": count - total,
            "percentage": percentage,
            "performance": performance
        })

    return jsonify({
        "level_finished": True,
        "completed_level": level_name,
        "completed_level_score": completed_level_score,
        **question_payload()
    })

if __name__ == "__main__":
    app.run(debug=True)
