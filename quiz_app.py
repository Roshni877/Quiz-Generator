import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
from data_loader import QuizDataLoader
from config import UI_SETTINGS

# Initialize data loader
data_loader = QuizDataLoader()
QUESTIONS = []
NUM_QUESTIONS = 0

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Smart Quiz Generator - Professional Edition")
        self.root.geometry(f"{UI_SETTINGS['window_width']}x{UI_SETTINGS['window_height']}")
        self.root.config(bg=UI_SETTINGS["bg_primary"])

        self.index = 0
        self.score = 0
        self.selected = tk.StringVar()
        self.user_answers = []
        self.current_category = "random"
        
        # Show loading screen first
        self.show_loading_screen()
        
    def show_loading_screen(self):
        """Show loading screen while fetching questions"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        frame.pack(fill="both", expand=True)
        
        tk.Label(
            frame,
            text="🎓 Quiz Generator",
            font=("Arial", 28, "bold"),
            bg=UI_SETTINGS["bg_primary"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=50)
        
        tk.Label(
            frame,
            text="Loading questions from database...",
            font=("Arial", 14),
            bg=UI_SETTINGS["bg_primary"],
            fg="#ffffff"
        ).pack(pady=20)
        
        # Progress bar
        progress = ttk.Progressbar(
            frame,
            length=300,
            mode="indeterminate"
        )
        progress.pack(pady=20)
        progress.start()
        
        self.root.update()
        
        # Load questions
        global QUESTIONS, NUM_QUESTIONS
        QUESTIONS = data_loader.fetch_questions(self.current_category)
        NUM_QUESTIONS = len(QUESTIONS)
        
        if NUM_QUESTIONS == 0:
            messagebox.showerror("Error", "Could not load questions. Make sure you have internet connection.")
            self.root.quit()
            return
        
        # Show category selection
        self.show_category_selection()
    
    def show_category_selection(self):
        """Let user select quiz category"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        tk.Label(
            frame,
            text="🎓 Select Quiz Category",
            font=("Arial", 22, "bold"),
            bg=UI_SETTINGS["bg_primary"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=20)
        
        tk.Label(
            frame,
            text="Choose a category or start with random questions",
            font=("Arial", 12),
            bg=UI_SETTINGS["bg_primary"],
            fg="#cccccc"
        ).pack(pady=10)
        
        categories = data_loader.get_categories()
        
        for category in categories:
            btn = tk.Button(
                frame,
                text=f"📚 {category.capitalize()}",
                command=lambda c=category: self.load_category(c),
                bg=UI_SETTINGS["bg_secondary"],
                fg="#ffffff",
                font=("Arial", 12),
                padx=20,
                pady=12,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(fill="x", pady=8)
    
    def load_category(self, category):
        """Load selected category and start quiz"""
        self.current_category = category
        self.index = 0
        self.score = 0
        self.selected.set("")
        self.user_answers = []
        
        # Show loading
        for widget in self.root.winfo_children():
            widget.destroy()
        
        loading = tk.Label(
            self.root,
            text=f"Loading {category.capitalize()} questions...",
            font=("Arial", 14),
            bg=UI_SETTINGS["bg_primary"],
            fg=UI_SETTINGS["color_accent"]
        )
        loading.pack(pady=250)
        
        self.root.update()
        
        # Fetch new questions
        global QUESTIONS, NUM_QUESTIONS
        QUESTIONS = data_loader.fetch_questions(category)
        NUM_QUESTIONS = len(QUESTIONS)
        
        if NUM_QUESTIONS == 0:
            messagebox.showerror("Error", "No questions available for this category.")
            self.show_category_selection()
            return
        
        # Build UI and start quiz
        self.build_ui()
        self.load_question()

    def build_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_header"], height=100)
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🎓 Smart Quiz Generator",
            font=("Arial", 24, "bold"),
            bg=UI_SETTINGS["bg_header"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=15)

        # Progress Frame
        progress_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_secondary"])
        progress_frame.pack(fill="x", padx=20, pady=10)

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Arial", 12),
            bg=UI_SETTINGS["bg_secondary"],
            fg=UI_SETTINGS["color_accent"]
        )
        self.progress_label.pack()

        # Question Frame
        question_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        question_frame.pack(fill="both", padx=30, pady=20)

        self.q_label = tk.Label(
            question_frame,
            text="",
            wraplength=750,
            font=("Arial", 16, "bold"),
            bg=UI_SETTINGS["bg_primary"],
            fg="#ffffff",
            justify="left"
        )
        self.q_label.pack(pady=20, anchor="w")

        # Options Frame
        options_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        options_frame.pack(fill="both", padx=40, pady=10)

        self.radio_buttons = []
        self.option_frames = []
        
        for i in range(4):
            opt_frame = tk.Frame(options_frame, bg=UI_SETTINGS["bg_secondary"], relief="flat", bd=2)
            opt_frame.pack(fill="x", pady=10)
            opt_frame.config(highlightthickness=1, highlightbackground=UI_SETTINGS["color_accent"])
            
            rb = tk.Radiobutton(
                opt_frame,
                text="",
                variable=self.selected,
                value="",
                font=("Arial", 13),
                bg=UI_SETTINGS["bg_secondary"],
                fg="#ffffff",
                activebackground=UI_SETTINGS["color_accent"],
                activeforeground=UI_SETTINGS["bg_primary"],
                selectcolor=UI_SETTINGS["color_accent"],
                anchor="w",
                padx=15,
                pady=10
            )
            rb.pack(fill="x", anchor="w")
            self.radio_buttons.append(rb)
            self.option_frames.append(opt_frame)

        # Feedback Frame
        self.feedback = tk.Label(
            self.root,
            text="",
            wraplength=750,
            font=("Arial", 11),
            bg=UI_SETTINGS["bg_primary"],
            fg="#ffffff"
        )
        self.feedback.pack(pady=10)

        # Button Frame
        button_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        button_frame.pack(pady=15)

        self.submit_btn = tk.Button(
            button_frame,
            text="Submit Answer",
            command=self.check_answer,
            bg=UI_SETTINGS["color_accent"],
            fg=UI_SETTINGS["bg_primary"],
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        self.submit_btn.pack(side="left", padx=10)

        self.next_btn = tk.Button(
            button_frame,
            text="Next Question →",
            command=self.next_question,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief="flat",
            state="disabled",
            cursor="hand2"
        )
        self.next_btn.pack(side="left", padx=10)

    def load_question(self):
        self.selected.set("")
        self.feedback.config(text="", fg="#ffffff")
        self.next_btn.config(state="disabled")
        self.submit_btn.config(state="normal")
        
        # Reset option frame colors
        for frame in self.option_frames:
            frame.config(highlightbackground="#00d4ff")

        q = QUESTIONS[self.index]
        
        # Update progress label
        self.progress_label.config(
            text=f"Question {self.index + 1} of {NUM_QUESTIONS}"
        )

        self.q_label.config(text=f"Q{self.index + 1}. {q['question']}")

        options = q["options"][:]
        random.shuffle(options)

        for i, opt in enumerate(options):
            self.radio_buttons[i].config(text=opt, value=opt)

    def check_answer(self):
        if not self.selected.get():
            messagebox.showwarning("Warning", "Please select an option!")
            return

        q = QUESTIONS[self.index]
        user_answer = self.selected.get()
        is_correct = user_answer == q["answer"]

        # Store answer for results
        self.user_answers.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

        if is_correct:
            self.score += 1
            self.feedback.config(
                text="✅ Correct!\n\n" + q["explanation"],
                fg="#00ff00"
            )
        else:
            self.feedback.config(
                text=f"❌ Wrong!\nCorrect Answer: {q['answer']}\n\n{q['explanation']}",
                fg="#ff6b6b"
            )

        self.next_btn.config(state="normal")
        self.submit_btn.config(state="disabled")

    def next_question(self):
        self.index += 1
        if self.index < len(QUESTIONS):
            self.load_question()
        else:
            self.show_result()

    def show_result(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Results Header
        header_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_header"], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🎉 Quiz Completed!",
            font=("Arial", 24, "bold"),
            bg=UI_SETTINGS["bg_header"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=20)

        # Score Frame
        score_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_secondary"])
        score_frame.pack(fill="x", padx=20, pady=15)

        percentage = (self.score / NUM_QUESTIONS) * 100
        grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 70 else "C" if percentage >= 60 else "D"
        
        score_text = f"Your Score: {self.score}/{NUM_QUESTIONS} ({percentage:.1f}%) | Grade: {grade}"
        tk.Label(
            score_frame,
            text=score_text,
            font=("Arial", 16, "bold"),
            bg=UI_SETTINGS["bg_secondary"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=10)

        # Results Details Frame with Scrollbar
        results_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        results_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Create a text widget with scrollbar
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side="right", fill="y")

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap="word",
            font=("Arial", 11),
            bg=UI_SETTINGS["bg_secondary"],
            fg="#ffffff",
            yscrollcommand=scrollbar.set,
            relief="flat",
            padx=10,
            pady=10
        )
        scrollbar.config(command=self.results_text.yview)
        self.results_text.pack(fill="both", expand=True)

        # Populate results
        for idx, answer in enumerate(self.user_answers, 1):
            status = "✅ CORRECT" if answer["is_correct"] else "❌ WRONG"
            self.results_text.insert("end", f"\nQ{idx}. {answer['question']}\n")
            self.results_text.insert("end", f"Status: {status}\n")
            self.results_text.insert("end", f"Your Answer: {answer['user_answer']}\n")
            
            if not answer["is_correct"]:
                self.results_text.insert("end", f"Correct Answer: {answer['correct_answer']}\n")
            
            self.results_text.insert("end", f"Explanation: {answer['explanation']}\n")
            self.results_text.insert("end", "-" * 80 + "\n")

        self.results_text.config(state="disabled")

        # Button Frame
        button_frame = tk.Frame(self.root, bg=UI_SETTINGS["bg_primary"])
        button_frame.pack(pady=15)

        restart_btn = tk.Button(
            button_frame,
            text="Try Another Category",
            command=self.restart_quiz,
            bg=UI_SETTINGS["color_accent"],
            fg=UI_SETTINGS["bg_primary"],
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        restart_btn.pack(side="left", padx=10)

        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        exit_btn.pack(side="left", padx=10)

    def restart_quiz(self):
        """Restart and show category selection"""
        self.show_category_selection()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
