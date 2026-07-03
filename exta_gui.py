import customtkinter as ctk
from tkinter import messagebox
import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import random
from datetime import datetime

# -------------------------
# Configuration
# -------------------------
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# -------------------------
# Question Bank (20 Questions)
# -------------------------
FULL_QUESTION_BANK = [
    # -- Original 15 --
    {"question": "What is the capital of India?", "options": ["Mumbai", "New Delhi", "Jaipur", "Chennai"], "answer": "New Delhi"},
    {"question": "What does CPU stand for?", "options": ["Central Processing Unit", "Computer Personal Unit", "Central Processor Utility", "Control Processing Unit"], "answer": "Central Processing Unit"},
    {"question": "2 + 2 × 3 = ?", "options": ["12", "8", "10", "6"], "answer": "8"},
    {"question": "Python is a ______ language.", "options": ["Low level", "Markup", "Programming", "Machine"], "answer": "Programming"},
    {"question": "Which is the largest planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Jupiter"},
    {"question": "RAM stands for?", "options": ["Random Access Memory", "Read Access Memory", "Run Any Memory", "Random Allowed Memory"], "answer": "Random Access Memory"},
    {"question": "Binary number system uses how many digits?", "options": ["10", "8", "4", "2"], "answer": "2"},
    {"question": "Which of the following is an output device?", "options": ["Mouse", "Keyboard", "Monitor", "Scanner"], "answer": "Monitor"},
    {"question": "Which data structure follows FIFO?", "options": ["Stack", "Queue", "Tree", "Graph"], "answer": "Queue"},
    {"question": "Shortcut key to copy?", "options": ["Ctrl + X", "Ctrl + V", "Ctrl + C", "Ctrl + A"], "answer": "Ctrl + C"},
    {"question": "Which scientist discovered gravity?", "options": ["Newton", "Einstein", "Edison", "Faraday"], "answer": "Newton"},
    {"question": "National animal of India?", "options": ["Peacock", "Tiger", "Elephant", "Lion"], "answer": "Tiger"},
    {"question": "Sun is a ______", "options": ["Planet", "Star", "Comet", "Asteroid"], "answer": "Star"},
    {"question": "HTML is used for?", "options": ["Programming", "Database", "Web page structure", "Networking"], "answer": "Web page structure"},
    {"question": "Which is smallest unit of data?", "options": ["Byte", "Bit", "Kilobyte", "Megabyte"], "answer": "Bit"},
    
    # -- New 5 Questions --
    {"question": "What is the chemical formula for water?", "options": ["CO2", "H2O", "O2", "NaCl"], "answer": "H2O"},
    {"question": "How many bytes are in 1 Kilobyte?", "options": ["1000", "1024", "100", "512"], "answer": "1024"},
    {"question": "Which component is the 'brain' of the computer?", "options": ["Monitor", "Keyboard", "CPU", "Mouse"], "answer": "CPU"},
    {"question": "What does HTTP stand for?", "options": ["Hyper Text Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Text Path", "None of these"], "answer": "Hyper Text Transfer Protocol"},
    {"question": "Which gas do humans inhale?", "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"], "answer": "Oxygen"}
]

# -------------------------
# Sound Manager (Robust)
# -------------------------
class SoundManager:
    def __init__(self):
        self.use_pygame = False
        try:
            import pygame
            pygame.mixer.init()
            self.use_pygame = True
        except ImportError:
            pass # Pygame not installed

    def play(self, sound_type):
        """Plays sound using Pygame (if valid files exist) or Winsound (fallback)."""
        # 1. Try Pygame with files
        if self.use_pygame:
            try:
                if sound_type == "click" and os.path.exists("click.wav"):
                    pygame.mixer.Sound("click.wav").play()
                    return
                elif sound_type == "correct" and os.path.exists("correct.wav"):
                    pygame.mixer.Sound("correct.wav").play()
                    return
                elif sound_type == "wrong" and os.path.exists("wrong.wav"):
                    pygame.mixer.Sound("wrong.wav").play()
                    return
            except:
                pass 
        
        # 2. Fallback to Windows System Beeps (Guaranteed sound on Windows)
        try:
            import winsound
            if sound_type == "correct":
                winsound.Beep(1000, 200) # High pitch for correct
            elif sound_type == "wrong":
                winsound.Beep(400, 400)  # Low pitch for wrong
            elif sound_type == "click":
                winsound.Beep(600, 50)   # Short beep for click
        except ImportError:
            pass # Not on Windows

# -------------------------
# Main Application
# -------------------------
class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("Quiz Master Pro")
        self.geometry("950x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State Variables
        self.sound = SoundManager()
        self.questions_pool = FULL_QUESTION_BANK
        self.current_session_questions = []
        self.current_q_index = 0
        self.score = 0
        self.start_time = 0
        self.student_name = ""
        self.history = []
        self.temp_session_answers = [] # Stores answers for the current session

        # -- Main Container --
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # -- Theme Toggle (Top Right) --
        self.theme_switch = ctk.CTkSwitch(self.main_frame, text="Dark Mode", command=self.toggle_theme, onvalue="on", offvalue="off")
        self.theme_switch.grid(row=0, column=0, sticky="ne", padx=20, pady=10)
        self.theme_switch.select() # Default to Dark

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
        ctk.CTkLabel(self.start_frame, text="5 Random Questions Challenge", font=("Roboto", 16), text_color="gray").pack(pady=(0, 40))
        
        self.name_entry = ctk.CTkEntry(self.start_frame, placeholder_text="Enter Candidate Name...", width=300, height=40, font=("Roboto", 14))
        self.name_entry.pack(pady=10)
        
        ctk.CTkButton(self.start_frame, text="Start Quiz", command=self.start_quiz, width=200, height=50, corner_radius=30, font=("Roboto", 16, "bold")).pack(pady=30)

        # 2. Quiz Screen
        self.quiz_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["quiz"] = self.quiz_frame
        
        self.progress_bar = ctk.CTkProgressBar(self.quiz_frame, width=500, height=15)
        self.progress_bar.pack(pady=(20, 10))
        
        self.progress_label = ctk.CTkLabel(self.quiz_frame, text="Question 1/5", font=("Roboto", 12))
        self.progress_label.pack(pady=(0, 20))

        self.q_card = ctk.CTkFrame(self.quiz_frame, fg_color=("gray90", "gray20"), corner_radius=15)
        self.q_card.pack(fill="x", padx=50, pady=10)
        
        self.q_label = ctk.CTkLabel(self.q_card, text="Question?", font=("Roboto Medium", 20), wraplength=700, pady=30)
        self.q_label.pack()

        self.options_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.options_frame.pack(pady=20)
        
        self.var = ctk.StringVar(value="-1")
        self.option_radios = []
        for i in range(4):
            # Using fixed values "0", "1", "2", "3" to avoid the CTK RadioButton error
            rb = ctk.CTkRadioButton(self.options_frame, text="Option", variable=self.var, value=str(i), 
                                    font=("Roboto", 16), width=300, height=40, corner_radius=10)
            rb.pack(pady=8)
            self.option_radios.append(rb)

        ctk.CTkButton(self.quiz_frame, text="Submit Answer", command=self.submit_answer, width=200, height=45, corner_radius=25, font=("Roboto", 14, "bold")).pack(pady=30)

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
            messagebox.showerror("Error", "Please enter name!")
            return
        
        self.student_name = name
        
        # Pick 5 random questions
        self.current_session_questions = random.sample(self.questions_pool, 5)
        
        self.current_q_index = 0
        self.score = 0
        self.temp_session_answers = [] 
        self.show_question()
        self.show_frame("quiz")
        self.sound.play("click")

    def show_question(self):
        if self.current_q_index >= len(self.current_session_questions):
            self.finish_quiz()
            return

        total = len(self.current_session_questions)
        self.progress_bar.set(self.current_q_index / total)
        self.progress_label.configure(text=f"Question {self.current_q_index + 1} of {total}")

        q_data = self.current_session_questions[self.current_q_index]
        self.q_label.configure(text=q_data['question'])
        
        self.var.set("-1") # Reset selection
        for i, option in enumerate(q_data['options']):
            self.option_radios[i].configure(text=option)

        self.start_time = time.time()

    def submit_answer(self):
        val = self.var.get()
        if val == "-1": 
            messagebox.showwarning("Select Option", "Please select an answer.")
            return
        
        selected_index = int(val)
        current_q = self.current_session_questions[self.current_q_index]
        selected_text = current_q['options'][selected_index]
        correct_answer = current_q["answer"]
        
        is_correct = (selected_text == correct_answer)
        
        if is_correct:
            self.score += 1
            self.sound.play("correct")
        else:
            self.sound.play("wrong")
            
        # Store for Excel
        self.temp_session_answers.append({
            "question": current_q['question'],
            "selected": selected_text,
            "correct_ans": correct_answer
        })
            
        self.current_q_index += 1
        self.show_question()

    def finish_quiz(self):
        self.progress_bar.set(1)
        total_q = len(self.current_session_questions)
        accuracy = round((self.score / total_q) * 100, 2)
        self.history.append(accuracy)

        # ---------------------------------------------------------
        #  EXCEL SAVING LOGIC (Robust)
        # ---------------------------------------------------------
        
        # 1. Prepare data (Flattened Row)
        row_data = {
            "Candidate Name": self.student_name,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Score": f"{self.score}/{total_q}",
            "Accuracy (%)": accuracy
        }

        # Add Q1-Q5 details dynamically
        for i, ans in enumerate(self.temp_session_answers):
            q_num = i + 1
            row_data[f"Q{q_num} Question"] = ans["question"]
            row_data[f"Q{q_num} Selected"] = ans["selected"]
            row_data[f"Q{q_num} Correct Answer"] = ans["correct_ans"]

        # 2. Convert to DataFrame
        new_df = pd.DataFrame([row_data])
        
        # 3. Define File Path (Absolute path prevents confusion)
        file_name = "quiz_results_flat.xlsx"
        file_path = os.path.abspath(file_name)
        
        print(f"Saving results to: {file_path}")

        # 4. Save Logic
        if os.path.exists(file_path):
            try:
                # Try reading existing file
                existing_df = pd.read_excel(file_path, engine='openpyxl')
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_excel(file_path, index=False, engine='openpyxl')
                print("Data appended successfully.")
            except Exception as e:
                # This catches if the file is corrupted (e.g. CSV renamed as XLSX)
                print(f"Error saving: {e}")
                messagebox.showerror("File Error", 
                    f"Could not save to Excel!\n\nPossible Reason: The file '{file_name}' might be corrupted or open.\n\n"
                    "Solution: Close the Excel file or Delete it so a new one can be created.")
        else:
            try:
                new_df.to_excel(file_path, index=False, engine='openpyxl')
                print("New Excel file created.")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not create file: {e}")

        # ---------------------------------------------------------

        self.score_label.configure(text=f"Final Score: {self.score} / {total_q}")
        
        if accuracy >= 80: self.msg_label.configure(text="🌟 Amazing Performance! 🌟", text_color="green")
        elif accuracy >= 50: self.msg_label.configure(text="👍 Good Effort!", text_color="orange")
        else: self.msg_label.configure(text="📚 Keep Practicing!", text_color="red")
        
        self.show_frame("result")
        self.plot_graph()

    def plot_graph(self):
        if not self.history: return
        attempts = list(range(1, len(self.history) + 1))
        
        # Plot logic
        plt.figure(figsize=(5, 4))
        plt.plot(attempts, self.history, marker="o", color='b')
        plt.title(f"Performance: {self.student_name}")
        plt.xlabel("Attempt")
        plt.ylabel("Accuracy %")
        plt.ylim(0, 105)
        plt.grid(True)
        plt.show()

    def restart_quiz(self):
        self.name_entry.delete(0, 'end')
        self.show_frame("start")

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()