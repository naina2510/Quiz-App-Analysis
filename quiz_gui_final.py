import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import random
import time
from datetime import datetime

# Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")
CREDENTIALS_FILE = "admin_credentials.xlsx"
DATA_FILE = "quiz_results_flat.xlsx"

# Question Bank
FULL_QUESTION_BANK = [
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
    {"question": "What is the chemical formula for water?", "options": ["CO2", "H2O", "O2", "NaCl"], "answer": "H2O"},
    {"question": "How many bytes are in 1 Kilobyte?", "options": ["1000", "1024", "100", "512"], "answer": "1024"},
    {"question": "Which component is the 'brain' of the computer?", "options": ["Monitor", "Keyboard", "CPU", "Mouse"], "answer": "CPU"},
    {"question": "What does HTTP stand for?", "options": ["Hyper Text Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Text Path", "None of these"], "answer": "Hyper Text Transfer Protocol"},
    {"question": "Which gas do humans inhale?", "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"], "answer": "Oxygen"}
]

# Sound Manager (Fixed)
class SoundManager:
    def __init__(self):
        self.use_pygame = False
        try:
            import pygame
            pygame.mixer.init()
            self.use_pygame = True
        except ImportError:
            pass

    def play(self, sound_type):
        played = False
        # 1. Try Pygame if available and file exists
        if self.use_pygame:
            try:
                if sound_type == "click" and os.path.exists("click.wav"):
                    pygame.mixer.Sound("click.wav").play()
                    played = True
                elif sound_type == "correct" and os.path.exists("correct.wav"):
                    pygame.mixer.Sound("correct.wav").play()
                    played = True
                elif sound_type == "wrong" and os.path.exists("wrong.wav"):
                    pygame.mixer.Sound("wrong.wav").play()
                    played = True
            except: pass
        
        # 2. Fallback to System Beep (Winsound) if file didn't play
        if not played:
            try:
                import winsound
                if sound_type == "correct": winsound.Beep(1000, 200) # High pitch
                elif sound_type == "wrong": winsound.Beep(400, 400)  # Low pitch
                elif sound_type == "click": winsound.Beep(600, 50)   # Short tick
            except: pass

# POPUP: ADD ADMIN
class AdminManagerPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Admin")
        self.geometry("400x350")
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text="Create Admin Account", font=("Roboto Medium", 20)).pack(pady=20)
        self.user_entry = ctk.CTkEntry(self, placeholder_text="New Username", width=250)
        self.user_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="New Password", show="*", width=250)
        self.pass_entry.pack(pady=10)
        ctk.CTkButton(self, text="Save Admin", command=self.add_admin, width=250, fg_color="#F39C12", hover_color="#D68910").pack(pady=20)
        self.status_label = ctk.CTkLabel(self, text="", text_color="green")
        self.status_label.pack(pady=10)
    def add_admin(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Fields cannot be empty")
            return
        new_data = pd.DataFrame([{"Username": str(username), "Password": str(password)}])
        if os.path.exists(CREDENTIALS_FILE):
            try:
                df = pd.read_excel(CREDENTIALS_FILE)
                df['Username'] = df['Username'].astype(str)
                if username in df['Username'].values:
                    messagebox.showerror("Error", "Username already exists!")
                    return
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_excel(CREDENTIALS_FILE, index=False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")
                return
        else:
            new_data.to_excel(CREDENTIALS_FILE, index=False)
        self.status_label.configure(text=f"Admin '{username}' added!")
        self.user_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')

# FRAME 1: QUIZ INTERFACE
class QuizFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_home):
        super().__init__(master)
        self.switch_to_home = switch_to_home
        self.sound = SoundManager()
        self.questions_pool = FULL_QUESTION_BANK
        self.frames = {}
        self.setup_start_screen()
        self.setup_quiz_screen()
        self.setup_result_screen()
        self.show_internal_frame("start")
    def show_internal_frame(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
    def setup_start_screen(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["start"] = frame
        ctk.CTkLabel(frame, text="QUIZ CHALLENGE", font=("Roboto Medium", 40)).pack(pady=(60, 10))
        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Enter Your Name...", width=300, height=40)
        self.name_entry.pack(pady=20)
        ctk.CTkButton(frame, text="Start Test", command=self.start_quiz, width=200, height=50, corner_radius=30).pack(pady=20)
        ctk.CTkButton(frame, text="Back to Menu", command=self.switch_to_home, width=200, fg_color="gray").pack()
    def setup_quiz_screen(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["quiz"] = frame
        self.progress_bar = ctk.CTkProgressBar(frame, width=500)
        self.progress_bar.pack(pady=(20, 10))
        self.progress_lbl = ctk.CTkLabel(frame, text="Q 1/5")
        self.progress_lbl.pack()
        self.q_label = ctk.CTkLabel(frame, text="Question", font=("Roboto", 20), wraplength=700)
        self.q_label.pack(pady=30)
        self.var = ctk.StringVar(value="-1")
        self.radios = []
        
        for i in range(4):
            r = ctk.CTkRadioButton(frame, text="", variable=self.var, value=str(i), width=300, height=30)
            r.pack(pady=5)
            self.radios.append(r)
        ctk.CTkButton(frame, text="Submit", command=self.submit_answer, width=200, height=45).pack(pady=30)

    def setup_result_screen(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["result"] = frame
        self.score_lbl = ctk.CTkLabel(frame, text="", font=("Roboto", 30))
        self.score_lbl.pack(pady=60)
        self.msg_lbl = ctk.CTkLabel(frame, text="", font=("Roboto", 18))
        self.msg_lbl.pack(pady=10)
        ctk.CTkButton(frame, text="Take Another Test", command=lambda: self.show_internal_frame("start"), fg_color="green").pack(pady=10)
        ctk.CTkButton(frame, text="Exit to Menu", command=self.switch_to_home, fg_color="red").pack(pady=10)

    def start_quiz(self):
        name = self.name_entry.get().strip()
        if not name: return
        self.student_name = name
        self.current_qs = random.sample(self.questions_pool, 5)
        self.q_idx = 0
        self.score = 0
        self.temp_answers = []
        self.show_question()
        self.show_internal_frame("quiz")
        self.sound.play("click")

    def show_question(self):
        if self.q_idx >= 5: self.finish_quiz(); return
        self.progress_bar.set(self.q_idx / 5)
        self.progress_lbl.configure(text=f"Question {self.q_idx + 1} of 5")
        q = self.current_qs[self.q_idx]
        self.q_label.configure(text=q['question'])
        self.var.set("-1")
        for i, opt in enumerate(q['options']): self.radios[i].configure(text=opt)

    def submit_answer(self):
        if self.var.get() == "-1": return
        q = self.current_qs[self.q_idx]
        sel_txt = q['options'][int(self.var.get())]
        corr = q['answer']
        if sel_txt == corr:
            self.score += 1
            self.sound.play("correct")
        else:
            self.sound.play("wrong")
        self.temp_answers.append({"q": q['question'], "sel": sel_txt, "corr": corr})
        self.q_idx += 1
        self.show_question()

    def finish_quiz(self):
        self.progress_bar.set(1)
        row = {"Candidate Name": self.student_name, "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Total Score": f"{self.score}/5", "Accuracy (%)": (self.score/5)*100}
        for i, ans in enumerate(self.temp_answers):
            n = i+1
            row[f"Q{n} Question"] = ans["q"]
            row[f"Q{n} Selected"] = ans["sel"]
            row[f"Q{n} Correct Answer"] = ans["corr"]
        df = pd.DataFrame([row])
        if os.path.exists(DATA_FILE):
            try: pd.concat([pd.read_excel(DATA_FILE), df], ignore_index=True).to_excel(DATA_FILE, index=False)
            except: pass
        else: df.to_excel(DATA_FILE, index=False)
        self.score_lbl.configure(text=f"Score: {self.score} / 5")
        self.msg_lbl.configure(text="Great Job!" if self.score >=3 else "Keep Practicing")
        self.show_internal_frame("result")

# FRAME 2: ANALYTICS DASHBOARD (Advanced v3.2)
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_home):
        super().__init__(master)
        self.switch_to_home = switch_to_home
        
        self.df = pd.DataFrame()
        self.current_display_df = pd.DataFrame()
        
        self.frames = {}
        self.setup_login_screen()
        self.setup_main_dashboard()
        self.show_internal_frame("login")

    def show_internal_frame(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def logout(self):
        self.user_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        self.status_lbl.configure(text="")
        self.show_internal_frame("login")

    def open_add_admin(self):
        AdminManagerPopup(self)

    # --- LOGIN ---
    def setup_login_screen(self):
        frame = ctk.CTkFrame(self)
        self.frames["login"] = frame
        
        bg = ctk.CTkFrame(frame, fg_color=("gray95", "gray10"))
        bg.place(relwidth=1, relheight=1)
        
        box = ctk.CTkFrame(frame, width=400, height=500, corner_radius=20, fg_color=("white", "gray20"))
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(box, text="ADMIN ACCESS", font=("Roboto Medium", 26)).pack(pady=(50, 30))
        self.user_entry = ctk.CTkEntry(box, placeholder_text="Username", width=280, height=45)
        self.user_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(box, placeholder_text="Password", show="*", width=280, height=45)
        self.pass_entry.pack(pady=10)
        ctk.CTkButton(box, text="SECURE LOGIN", command=self.check_login, width=280, height=50).pack(pady=30)
        ctk.CTkButton(box, text="Back to Home", command=self.switch_to_home, width=280, fg_color="gray").pack(pady=10)
        self.status_lbl = ctk.CTkLabel(box, text="", text_color="red")
        self.status_lbl.pack()

    def check_login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        if not os.path.exists(CREDENTIALS_FILE):
            self.status_lbl.configure(text="Error: Credentials file missing!")
            return
        try:
            df = pd.read_excel(CREDENTIALS_FILE)
            df['Username'] = df['Username'].astype(str).str.strip()
            df['Password'] = df['Password'].astype(str).str.strip()
            if not df[(df['Username'] == user) & (df['Password'] == pwd)].empty:
                self.load_data()
                self.show_internal_frame("dashboard")
            else:
                self.status_lbl.configure(text="Invalid Username or Password")
        except Exception as e:
            self.status_lbl.configure(text=f"Error: {e}")

    # --- DASHBOARD UI ---
    def setup_main_dashboard(self):
        frame = ctk.CTkFrame(self)
        self.frames["dashboard"] = frame
        
        top_bar = ctk.CTkFrame(frame, height=70, corner_radius=0)
        top_bar.pack(fill="x", side="top")
        
        ctk.CTkLabel(top_bar, text="📊 Pro Analytics Suite", font=("Roboto Medium", 24)).pack(side="left", padx=30)
        
        ctk.CTkButton(top_bar, text="Logout", command=self.logout, width=100, fg_color="#E45756").pack(side="right", padx=10)
        ctk.CTkButton(top_bar, text="Add Admin", command=self.open_add_admin, width=120, fg_color="#F39C12").pack(side="right", padx=10)
        ctk.CTkButton(top_bar, text="Refresh", command=self.load_data, width=100, fg_color="#3498DB").pack(side="right", padx=10)

        self.tabs = ctk.CTkTabview(frame)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabs.add(" Overview "); self.tabs.add(" Detailed Analysis "); self.tabs.add(" Records & Export ")
        
        self.setup_overview(self.tabs.tab(" Overview "))
        self.setup_analysis(self.tabs.tab(" Detailed Analysis "))
        self.setup_records(self.tabs.tab(" Records & Export "))

    def setup_overview(self, frame):
        self.kpi_frame = ctk.CTkFrame(frame, fg_color="transparent"); self.kpi_frame.pack(fill="x", pady=15)
        charts = ctk.CTkFrame(frame, fg_color="transparent"); charts.pack(fill="both", expand=True)
        self.chart_l = ctk.CTkFrame(charts); self.chart_l.pack(side="left", fill="both", expand=True, padx=(0,5))
        self.chart_r = ctk.CTkFrame(charts); self.chart_r.pack(side="right", fill="both", expand=True, padx=(5,0))

    def setup_analysis(self, frame):
        self.hardest_frame = ctk.CTkFrame(frame); self.hardest_frame.pack(fill="both", expand=True, pady=(0,10))
        self.trend_frame = ctk.CTkFrame(frame); self.trend_frame.pack(fill="both", expand=True, pady=(10,0))

    def setup_records(self, frame):
        ctrl = ctk.CTkFrame(frame, height=50); ctrl.pack(fill="x", pady=10)
        self.search_entry = ctk.CTkEntry(ctrl, placeholder_text="Search Name...", width=250)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(ctrl, text="Search", command=self.filter_data, width=80).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="Export Excel", command=self.export_data, fg_color="green").pack(side="right", padx=10)
        
        self.tree_frame = ctk.CTkFrame(frame); self.tree_frame.pack(fill="both", expand=True)
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white", rowheight=25)
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "Date", "Score", "Accuracy"), show="headings")
        for c in ("Name", "Date", "Score", "Accuracy"): self.tree.heading(c, text=c); self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True)

    # --- LOGIC ---
    def load_data(self):
        if not os.path.exists(DATA_FILE): return
        try: self.df = pd.read_excel(DATA_FILE); self.refresh_ui()
        except: pass

    def refresh_ui(self):
        # KPIs
        for w in self.kpi_frame.winfo_children(): w.destroy()
        tot = len(self.df); avg = self.df["Accuracy (%)"].mean() if tot>0 else 0
        pas = len(self.df[self.df["Accuracy (%)"] >= 50])
        self.add_kpi("Total", tot, "#3498DB"); self.add_kpi("Avg %", f"{avg:.1f}%", "#F1C40F"); self.add_kpi("Pass", pas, "#2ECC71")
        
        # Charts
        self.plot_hist(self.chart_l); self.plot_pie(self.chart_r)
        self.plot_hardest(self.hardest_frame); self.plot_trend(self.trend_frame)
        self.populate_table()

    def add_kpi(self, t, v, c):
        f = ctk.CTkFrame(self.kpi_frame, fg_color=c); f.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(f, text=t, text_color="white", font=("bold", 14)).pack(pady=5)
        ctk.CTkLabel(f, text=str(v), text_color="white", font=("bold", 24)).pack(pady=5)

    def plot_hist(self, parent):
        for w in parent.winfo_children(): w.destroy()
        fig = plt.Figure(figsize=(4,3), dpi=100)
        ax = fig.add_subplot(111)
        ax.hist(self.df["Accuracy (%)"], bins=10, color="skyblue", edgecolor="white")
        ax.set_title("Score Distribution")
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(fill="both", expand=True)

    def plot_pie(self, parent):
        for w in parent.winfo_children(): w.destroy()
        fig = plt.Figure(figsize=(4,3), dpi=100)
        ax = fig.add_subplot(111)
        pas = len(self.df[self.df["Accuracy (%)"]>=50]); fai = len(self.df)-pas
        if len(self.df)>0: ax.pie([pas, fai], labels=['Pass', 'Fail'], autopct='%1.1f%%', colors=['#2ECC71', '#E74C3C'])
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(fill="both", expand=True)

    def plot_hardest(self, parent):
        for w in parent.winfo_children(): w.destroy()
        q_stats = {}
        for _, row in self.df.iterrows():
            for i in range(1, 6):
                q = row.get(f"Q{i} Question"); sel = row.get(f"Q{i} Selected"); ans = row.get(f"Q{i} Correct Answer")
                if pd.isna(q): continue
                if q not in q_stats: q_stats[q] = {'w':0, 't':0}
                q_stats[q]['t']+=1
                if str(sel).strip() != str(ans).strip(): q_stats[q]['w']+=1
        
        d = [{'Q': k[:40]+"...", 'Err': (v['w']/v['t'])*100} for k,v in q_stats.items() if v['t']>0]
        if not d: return
        qdf = pd.DataFrame(d).sort_values("Err").tail(5)
        
        fig = plt.Figure(figsize=(8,3), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(qdf['Q'], qdf['Err'], color="#E74C3C")
        ax.set_title("Hardest Questions (Error Rate %)")
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(fill="both", expand=True)

    def plot_trend(self, parent):
        for w in parent.winfo_children(): w.destroy()
        try:
            temp = self.df.copy(); temp['D'] = pd.to_datetime(temp['Date'], errors='coerce')
            daily = temp.groupby(temp['D'].dt.date)['Accuracy (%)'].mean()
            if daily.empty: return
            fig = plt.Figure(figsize=(8,3), dpi=100)
            ax = fig.add_subplot(111)
            daily.plot(kind='line', marker='o', ax=ax, color='purple')
            ax.set_title("Daily Average Performance")
            FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(fill="both", expand=True)
        except: pass

    def populate_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.current_display_df = self.df.sort_values("Date", ascending=False)
        for _, r in self.current_display_df.iterrows():
            self.tree.insert("", "end", values=(r["Candidate Name"], r["Date"], r["Total Score"], r["Accuracy (%)"]))

    def filter_data(self):
        q = self.search_entry.get().lower()
        for i in self.tree.get_children(): self.tree.delete(i)
        f = self.df[self.df["Candidate Name"].astype(str).str.lower().str.contains(q)]
        for _, r in f.iterrows(): self.tree.insert("", "end", values=(r["Candidate Name"], r["Date"], r["Total Score"], r["Accuracy (%)"]))
        self.current_display_df = f

    def export_data(self):
        if self.current_display_df.empty: return
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if f: self.current_display_df.to_excel(f, index=False)

# MAIN APP CONTAINER
class UnifiedApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quiz & Analytics Suite v4.0")
        self.geometry("1200x800")
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        self.frames["home"] = self.create_home()
        self.frames["quiz"] = QuizFrame(self.container, lambda: self.show("home"))
        self.frames["admin"] = DashboardFrame(self.container, lambda: self.show("home"))
        
        self.show("home")

    def create_home(self):
        f = ctk.CTkFrame(self.container)
        ctk.CTkLabel(f, text="Quiz Master Suite", font=("Roboto Medium", 40)).pack(pady=(100, 50))
        ctk.CTkButton(f, text="🎓 Take Test", command=lambda: self.show("quiz"), width=300, height=80, font=("bold", 20)).pack(pady=20)
        ctk.CTkButton(f, text="📊 Admin Dashboard", command=lambda: self.show("admin"), width=300, height=80, font=("bold", 20), fg_color="gray").pack(pady=20)
        return f

    def show(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

if __name__ == "__main__":
    app = UnifiedApp()
    app.mainloop()