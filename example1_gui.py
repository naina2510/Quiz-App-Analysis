import tkinter as tk
from tkinter import messagebox
import time
import pandas as pd
import matplotlib.pyplot as plt
# -------------------------
# Questions bank (15 MCQs)
# -------------------------
questions = [
    {"question": "What is the capital of India?",
     "options": ["Mumbai", "New Delhi", "Jaipur", "Chennai"],
     "answer": "New Delhi"},

    {"question": "What does CPU stand for?",
     "options": ["Central Processing Unit", "Computer Personal Unit", "Central Processor Utility", "Control Processing Unit"],
     "answer": "Central Processing Unit"},

    {"question": "2 + 2 × 3 = ?",
     "options": ["12", "8", "10", "6"],
     "answer": "8"},

    {"question": "Python is a ______ language.",
     "options": ["Low level", "Markup", "Programming", "Machine"],
     "answer": "Programming"},

    {"question": "Which is the largest planet?",
     "options": ["Earth", "Mars", "Jupiter", "Venus"],
     "answer": "Jupiter"},

    {"question": "RAM stands for?",
     "options": ["Random Access Memory", "Read Access Memory", "Run Any Memory", "Random Allowed Memory"],
     "answer": "Random Access Memory"},

    {"question": "Binary number system uses how many digits?",
     "options": ["10", "8", "4", "2"],
     "answer": "2"},

    {"question": "Which of the following is an output device?",
     "options": ["Mouse", "Keyboard", "Monitor", "Scanner"],
     "answer": "Monitor"},

    {"question": "Which data structure follows FIFO?",
     "options": ["Stack", "Queue", "Tree", "Graph"],
     "answer": "Queue"},

    {"question": "Shortcut key to copy?",
     "options": ["Ctrl + X", "Ctrl + V", "Ctrl + C", "Ctrl + A"],
     "answer": "Ctrl + C"},

    {"question": "Which scientist discovered gravity?",
     "options": ["Newton", "Einstein", "Edison", "Faraday"],
     "answer": "Newton"},

    {"question": "National animal of India?",
     "options": ["Peacock", "Tiger", "Elephant", "Lion"],
     "answer": "Tiger"},

    {"question": "Sun is a ______",
     "options": ["Planet", "Star", "Comet", "Asteroid"],
     "answer": "Star"},

    {"question": "HTML is used for?",
     "options": ["Programming", "Database", "Web page structure", "Networking"],
     "answer": "Web page structure"},

    {"question": "Which is smallest unit of data?",
     "options": ["Byte", "Bit", "Kilobyte", "Megabyte"],
     "answer": "Bit"}
]
# -------------------------
# Global variables
# -------------------------
current_q = 0
score = 0
start_time = 0
time_per_question = []
history = []
student_name = ""
# -------------------------
# Restart Quiz
# -------------------------
def restart_quiz():
    global current_q, score, time_per_question, student_name
    current_q = 0
    score = 0
    time_per_question = []
    student_name = ""
    result_frame.pack_forget()
    quiz_frame.pack_forget()
    name_entry.delete(0, tk.END)
    start_frame.pack(fill="both", expand=True)
# -------------------------
# Close App
# -------------------------
def close_app():
    root.destroy()
# -------------------------
# Start quiz after name entry
# -------------------------
def start_quiz():
    global student_name
    student_name = name_entry.get().strip()
    if student_name == "":
        messagebox.showerror("Error", "Please enter your name first")
        return
    start_frame.pack_forget()
    quiz_frame.pack(fill="both", expand=True)
    show_question()
# -------------------------
# Timer
# -------------------------
def start_timer():
    global start_time
    start_time = time.time()
# -------------------------
# Show question
# -------------------------
def show_question():
    global current_q
    if current_q >= len(questions):
        finish_quiz()
        return
    q_label.config(text=f"Q{current_q+1}: {questions[current_q]['question']}")
    var.set(None)
    for i in range(4):
        options[i].config(text=questions[current_q]["options"][i],
                          value=questions[current_q]["options"][i])
    start_timer()
# -------------------------
# Submit answer
# -------------------------
def submit_answer():
    global current_q, score
    if var.get() == "":
        messagebox.showwarning("Warning", "Please select an answer")
        return
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    time_per_question.append(time_taken)
    if var.get() == questions[current_q]["answer"]:
        score += 1
    current_q += 1
    show_question()
# -------------------------
# Finish quiz
# -------------------------
def finish_quiz():
    global current_q, score
    accuracy = round((score / len(questions)) * 100, 2)
    history.append(accuracy)
    df = pd.DataFrame({
        "name": [student_name] * len(questions),
        "question": [q["question"] for q in questions],
        "time_taken_sec": time_per_question
    })
    df.to_csv("quiz_results.csv", mode="a", index=False)
    quiz_frame.pack_forget()
    result_frame.pack(fill="both", expand=True)
    result_label.config(
        text=f"Name: {student_name}\nScore: {score}/{len(questions)}\nAccuracy: {accuracy}%"
    )
    attempts = list(range(1, len(history)+1))
    plt.figure()
    plt.plot(attempts, history, marker="o")
    plt.xlabel("Attempt")
    plt.ylabel("Accuracy (%)")
    plt.title(f"Learning Curve for {student_name}")
    plt.grid(True)
    plt.show()
# -------------------------
# GUI Window
# -------------------------
root = tk.Tk()
root.title("Quiz App with Performance Analysis")
root.geometry("700x500")
# -------------------------
# Start Frame
# -------------------------
start_frame = tk.Frame(root)
start_frame.pack(fill="both", expand=True)
title = tk.Label(start_frame, text="Quiz App with Performance Analysis",
                 font=("Arial", 18))
title.pack(pady=20)
name_label = tk.Label(start_frame, text="Enter your name:", font=("Arial", 12))
name_label.pack()
name_entry = tk.Entry(start_frame, font=("Arial", 12))
name_entry.pack(pady=10)
start_button = tk.Button(start_frame, text="Start Quiz",
                         command=start_quiz, font=("Arial", 12))
start_button.pack(pady=20)
# -------------------------
# Quiz Frame
# -------------------------
quiz_frame = tk.Frame(root)
q_label = tk.Label(quiz_frame, text="", font=("Arial", 14), wraplength=600)
q_label.pack(pady=20)
var = tk.StringVar(value="")
options = []
for i in range(4):
    rb = tk.Radiobutton(quiz_frame, text="", variable=var, value="",
                        font=("Arial", 12))
    rb.pack(anchor="w")
    options.append(rb)
submit_btn = tk.Button(quiz_frame, text="Submit",
                       command=submit_answer, font=("Arial", 12))
submit_btn.pack(pady=20)
# -------------------------
# Result Frame
# -------------------------
result_frame = tk.Frame(root)
result_label = tk.Label(result_frame, text="", font=("Arial", 14))
result_label.pack(pady=20)
restart_btn = tk.Button(result_frame, text="Restart Quiz",
                        command=restart_quiz, font=("Arial", 12))
restart_btn.pack(pady=10)
close_btn = tk.Button(result_frame, text="Close",
                      command=close_app, font=("Arial", 12))
close_btn.pack(pady=10)
root.mainloop()
