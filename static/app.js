const welcome = document.getElementById("welcome");
const quiz = document.getElementById("quiz");
const result = document.getElementById("result");
const startBtn = document.getElementById("startBtn");
const restartBtn = document.getElementById("restartBtn");
const nextBtn = document.getElementById("nextBtn");
const optionsBox = document.getElementById("options");
const feedback = document.getElementById("feedback");
let answered = false;

async function api(url, method = "GET", body = null) {
  const response = await fetch(url, {
    method,
    headers: body ? {"Content-Type": "application/json"} : {},
    body: body ? JSON.stringify(body) : null
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function showScreen(screen) {
  [welcome, quiz, result].forEach(el => el.classList.add("hidden"));
  screen.classList.remove("hidden");
}

async function startQuiz() {
  try {
    const data = await api("/api/start", "POST", {});
    showScreen(quiz);
    renderQuestion(data);
  } catch (error) { alert(error.message); }
}

function renderQuestion(data) {
  answered = false;
  nextBtn.disabled = true;
  nextBtn.innerHTML = 'Continue <span>→</span>';
  feedback.className = "feedback hidden";
  feedback.innerHTML = "";
  document.getElementById("levelTitle").textContent = data.level_name;
  document.getElementById("questionNumber").textContent = String(data.question_number).padStart(2, "0");
  document.getElementById("questionTotal").textContent = `/ ${String(data.level_total).padStart(2, "0")}`;
  document.getElementById("questionLabel").textContent = `QUESTION ${String(data.question_number).padStart(2, "0")}`;
  document.getElementById("questionText").textContent = data.question;
  document.getElementById("progressBar").style.width = `${((data.question_number - 1) / data.level_total) * 100}%`;
  document.getElementById("scorePreview").textContent = `SCORE: ${data.total_score}`;
  [1,2,3].forEach(n => {
    const step = document.getElementById(`step${n}`);
    step.classList.toggle("active", n === data.level);
    step.classList.toggle("complete", n < data.level);
  });
  optionsBox.innerHTML = "";
  Object.entries(data.options).forEach(([key, value]) => {
    const button = document.createElement("button");
    button.className = "option";
    button.type = "button";
    button.innerHTML = `<span class="option-key">${key}</span><span></span>`;
    button.querySelector("span:last-child").textContent = value;
    button.addEventListener("click", () => chooseAnswer(key, button));
    optionsBox.appendChild(button);
  });
}

async function chooseAnswer(choice, selectedButton) {
  if (answered) return;
  try {
    const data = await api("/api/answer", "POST", {answer: choice});
    answered = true;
    [...optionsBox.children].forEach(button => {
      button.disabled = true;
      const key = button.querySelector(".option-key").textContent;
      if (key === data.correct_answer) button.classList.add("correct");
      else if (button === selectedButton && !data.correct) button.classList.add("wrong");
    });
    feedback.className = `feedback ${data.correct ? "" : "incorrect"}`;
    feedback.innerHTML = `<strong>${data.correct ? "✓ Correct answer!" : "✕ Not quite — the correct answer is " + data.correct_answer + "."}</strong>`;
    const explanation = document.createElement("span");
    explanation.textContent = data.explanation;
    feedback.appendChild(explanation);
    nextBtn.disabled = false;
    nextBtn.innerHTML = 'Next question <span>→</span>';
    document.getElementById("scorePreview").textContent = `SCORE: ${data.total_score}`;
    document.getElementById("answerHint").textContent = data.correct ? "NICE WORK — KEEP GOING" : "LEARN FROM THE EXPLANATION";
  } catch (error) { alert(error.message); }
}

async function nextQuestion() {
  try {
    const data = await api("/api/next", "POST", {});
    if (data.done) {
      showResult(data);
      return;
    }
    if (data.level_finished) {
      alert(`${data.completed_level} completed! Score: ${data.completed_level_score}/5. Next level unlocked.`);
    }
    renderQuestion(data);
  } catch (error) { alert(error.message); }
}

function showResult(data) {
  showScreen(result);
  document.getElementById("finalScore").textContent = data.total_score;
  document.getElementById("correctCount").textContent = data.total_score;
  document.getElementById("wrongCount").textContent = data.wrong_answers;
  document.getElementById("percentage").textContent = `${data.percentage}%`;
  document.getElementById("performance").textContent = data.performance;
  document.getElementById("resultTitle").textContent = data.percentage >= 80 ? "Outstanding work!" : data.percentage >= 60 ? "Well played." : "Keep building.";
  document.querySelector(".score-number span").textContent = `/ ${data.total_questions}`;
  document.getElementById("resultBar").style.width = `${data.percentage}%`;
}

startBtn.addEventListener("click", startQuiz);
restartBtn.addEventListener("click", startQuiz);
nextBtn.addEventListener("click", nextQuestion);
