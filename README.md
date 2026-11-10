# Python Quiz Master

A polished, responsive web version of your Python quiz, built with **Python + Flask + HTML + CSS + JavaScript**.

## Features
- Three levels: Beginner, Intermediate, Advanced
- Five questions in each level
- A/B/C/D answer selection with input validation
- Instant correct/incorrect feedback and explanations
- Level-wise progress and final score summary
- Restart option
- Responsive layout for desktop and mobile

## Run on Windows
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open the terminal in this folder and run:

   ```bash
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

If `py` does not work, use `python` instead.

## Project structure

```text
Python_Quiz_Master/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

The questions and answer checking are handled by Python. HTML provides the page structure, CSS handles the design, and JavaScript handles browser interactions.
