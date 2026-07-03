import customtkinter as ctk
from tkinter import messagebox
import time
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------
# Configuration
# -------------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

QUESTIONS_DATA =  [
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
# Sound Manager
# -------------------------
class SoundManager:
    def __init__(self):
        self.sound_enabled = PYGAME_AVAILABLE
        if self.sound_enabled:
            pygame.mixer.init()

    def play(self, sound_type):
        if not self.sound_enabled: return
        try:
            # Placeholder for sound logic
            pass 
        except:
            pass

# -------------------------
# Main Application
# -------------------------
class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Quiz Master Pro")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Managers
        self.sound = SoundManager()
        self.questions = QUESTIONS_DATA
        self.current_q_index = 0
        self.score = 0
        self.start_time = 0
        self.time_per_question = []
        self.student_name = ""
        self.history = []

        # -- Main Container --
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # -- Top Bar --
        self.top_bar = ctk.CTkFrame(self.main_frame, height=50, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        self.theme_switch = ctk.CTkSwitch(self.top_bar, text="Dark Mode", command=self.toggle_theme, onvalue="on", offvalue="off")
        self.theme_switch.select() 
        self.theme_switch.pack(side="right")

        self.frames = {}
        self.setup_screens()
        self.show_frame("start")

    def toggle_theme(self):
        if self.theme_switch.get() == "on":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        self.sound.play("click")

    def setup_screens(self):
        # 1. Start Screen
        self.start_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["start"] = self.start_frame
        
        ctk.CTkLabel(self.start_frame, text="QUIZ MASTER", font=("Roboto Medium", 40)).pack(pady=(60, 10))
        ctk.CTkLabel(self.start_frame, text="Test your knowledge", font=("Roboto", 16), text_color="gray").pack(pady=(0, 40))
        
        self.name_entry = ctk.CTkEntry(self.start_frame, placeholder_text="Enter your name...", width=300, height=40, font=("Roboto", 14))
        self.name_entry.pack(pady=10)
        
        ctk.CTkButton(self.start_frame, text="Start Quiz", command=self.start_quiz, width=200, height=50, font=("Roboto", 16, "bold"), corner_radius=30).pack(pady=30)

        # 2. Quiz Screen
        self.quiz_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["quiz"] = self.quiz_frame
        
        self.progress_bar = ctk.CTkProgressBar(self.quiz_frame, width=500, height=15)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 10))
        
        self.progress_label = ctk.CTkLabel(self.quiz_frame, text="Question 1/5", font=("Roboto", 12))
        self.progress_label.pack(pady=(0, 20))

        self.q_card = ctk.CTkFrame(self.quiz_frame, fg_color=("gray90", "gray20"), corner_radius=15)
        self.q_card.pack(fill="x", padx=50, pady=10)
        
        self.q_label = ctk.CTkLabel(self.q_card, text="Question?", font=("Roboto Medium", 20), wraplength=700, pady=30)
        self.q_label.pack()

        self.options_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.options_frame.pack(pady=20)
        
        # Use a generic variable, we will store INDICES (0, 1, 2, 3) instead of text values
        self.var = ctk.StringVar(value="-1") 
        self.option_radios = []
        
        for i in range(4):
            # FIXED: We assign a static value (str(i)) that never changes. 
            # We only update the text later.
            rb = ctk.CTkRadioButton(self.options_frame, text="Option", variable=self.var, value=str(i), 
                                    font=("Roboto", 16), width=300, height=40, corner_radius=10)
            rb.pack(pady=8)
            self.option_radios.append(rb)

        ctk.CTkButton(self.quiz_frame, text="Submit Answer", command=self.submit_answer, width=200, height=45, corner_radius=25).pack(pady=30)

        # 3. Result Screen
        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["result"] = self.result_frame

        self.score_label = ctk.CTkLabel(self.result_frame, text="Score: 0/0", font=("Roboto Medium", 35))
        self.score_label.pack(pady=(80, 20))
        
        self.msg_label = ctk.CTkLabel(self.result_frame, text="Great Job!", font=("Roboto", 18), text_color="gray")
        self.msg_label.pack(pady=(0, 40))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.pack()
        
        ctk.CTkButton(btn_row, text="Play Again", command=self.restart_quiz, fg_color="green", width=150, height=40).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Exit", command=self.destroy, fg_color="red", width=150, height=40).pack(side="left", padx=10)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[name].grid(row=1, column=0, sticky="nsew")

    # -------------------------
    # Game Logic
    # -------------------------
    def start_quiz(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name required!")
            return
        
        self.student_name = name
        self.current_q_index = 0
        self.score = 0
        self.time_per_question = []
        self.show_question()
        self.show_frame("quiz")
        self.sound.play("click")

    def show_question(self):
        if self.current_q_index >= len(self.questions):
            self.finish_quiz()
            return

        progress = self.current_q_index / len(self.questions)
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Question {self.current_q_index + 1} of {len(self.questions)}")

        q_data = self.questions[self.current_q_index]
        self.q_label.configure(text=q_data['question'])
        
        # Reset selection to a value that doesn't exist (e.g. "-1")
        self.var.set("-1")
        
        for i, option in enumerate(q_data['options']):
            # FIXED: We ONLY configure 'text'. We do NOT configure 'value'.
            self.option_radios[i].configure(text=option)

        self.start_time = time.time()

    def submit_answer(self):
        selected_index_str = self.var.get()
        
        # Check if user selected nothing (value will be "-1")
        if selected_index_str == "-1": 
            return
        
        time_taken = round(time.time() - self.start_time, 2)
        self.time_per_question.append(time_taken)

        # Logic: Convert index string "0"/"1" back to integer, then get the text option
        selected_index = int(selected_index_str)
        selected_text = self.questions[self.current_q_index]['options'][selected_index]
        correct_answer = self.questions[self.current_q_index]["answer"]

        if selected_text == correct_answer:
            self.score += 1
            self.sound.play("correct")
        else:
            self.sound.play("wrong")
            
        self.current_q_index += 1
        self.show_question()

    def finish_quiz(self):
        self.progress_bar.set(1)
        accuracy = round((self.score / len(self.questions)) * 100, 2)
        self.history.append(accuracy)

        data = {
            "name": [self.student_name] * len(self.questions),
            "question": [q["question"] for q in self.questions],
            "time_taken_sec": self.time_per_question
        }
        df = pd.DataFrame(data)
        header = not os.path.exists("quiz_results.csv")
        df.to_csv("quiz_results.csv", mode="a", index=False, header=header)

        self.score_label.configure(text=f"Final Score: {self.score} / {len(self.questions)}")
        
        if accuracy >= 80: self.msg_label.configure(text="🌟 Amazing Performance! 🌟", text_color="green")
        elif accuracy >= 50: self.msg_label.configure(text="👍 Good Effort!", text_color="orange")
        else: self.msg_label.configure(text="📚 Keep Practicing!", text_color="red")
        
        self.show_frame("result")
        self.plot_graph()

    def plot_graph(self):
        attempts = list(range(1, len(self.history) + 1))
        plt.figure(figsize=(5, 4))
        plt.plot(attempts, self.history, marker="o")
        plt.title(f"Progress for {self.student_name}")
        plt.xlabel("Attempt")
        plt.ylabel("Accuracy %")
        plt.grid()
        plt.show()

    def restart_quiz(self):
        self.name_entry.delete(0, 'end')
        self.show_frame("start")

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()