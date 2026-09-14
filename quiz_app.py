import tkinter as tk
from tkinter import messagebox, ttk
import random
from data_loader import QuizDataLoader
from config import UI_SETTINGS

# Initialize data loader
data_loader = QuizDataLoader()

class ScrollableFrame(tk.Frame):
    """
    A reusable Scrollable Frame for Tkinter supporting smooth mouse wheel scrolling
    on Windows, macOS, and Linux, with automatic width wrapping.
    """
    def __init__(self, parent, bg_color=UI_SETTINGS["bg_primary"], *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)
        self.bg_color = bg_color
        
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=bg_color)
        
        self.content.bind(
            "<Configure>",
            self._on_content_configure
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel events across window
        self._bind_mousewheel_recursive(self)
        
    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel_recursive(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel_up, add="+")
        widget.bind("<Button-5>", self._on_mousewheel_down, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_up(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(1, "units")


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Smart Quiz Generator - Professional Edition")
        self.root.geometry(f"{UI_SETTINGS['window_width']}x{UI_SETTINGS['window_height']}")
        self.root.minsize(650, 500)
        self.root.config(bg=UI_SETTINGS["bg_primary"])

        self.index = 0
        self.score = 0
        self.selected = tk.StringVar()
        self.user_answers = []
        self.current_category = "random"
        self.questions = []
        self.num_questions = 0
        
        # Start immediately with category selection
        self.show_category_selection()
        
    def clear_root(self):
        """Destroy all current widgets on root"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_category_selection(self):
        """Let user select quiz category with full scrollability"""
        self.clear_root()
        
        scroll_frame = ScrollableFrame(self.root, bg_color=UI_SETTINGS["bg_primary"])
        scroll_frame.pack(fill="both", expand=True)
        container = scroll_frame.content
        
        # Header
        header_frame = tk.Frame(container, bg=UI_SETTINGS["bg_header"], pady=20)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text="🎓 Smart Quiz Generator",
            font=("Segoe UI", 24, "bold"),
            bg=UI_SETTINGS["bg_header"],
            fg=UI_SETTINGS["color_accent"]
        ).pack()

        tk.Label(
            header_frame,
            text="Choose a category to start your instant quiz",
            font=("Segoe UI", 12),
            bg=UI_SETTINGS["bg_header"],
            fg="#cccccc"
        ).pack(pady=5)
        
        # Category list frame
        cat_box = tk.Frame(container, bg=UI_SETTINGS["bg_primary"], padx=30, pady=20)
        cat_box.pack(fill="both", expand=True)
        
        categories = data_loader.get_categories()
        
        for category in categories:
            cat_card = tk.Frame(cat_box, bg=UI_SETTINGS["bg_secondary"], bd=1, relief="solid")
            cat_card.pack(fill="x", pady=6)
            cat_card.config(highlightthickness=1, highlightbackground=UI_SETTINGS["color_accent"])

            btn = tk.Button(
                cat_card,
                text=f"📚  {category.capitalize()} Quiz",
                command=lambda c=category: self.load_category(c),
                bg=UI_SETTINGS["bg_secondary"],
                fg="#ffffff",
                activebackground=UI_SETTINGS["color_accent"],
                activeforeground=UI_SETTINGS["bg_primary"],
                font=("Segoe UI", 13, "bold"),
                anchor="w",
                padx=20,
                pady=14,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(fill="x", expand=True)
            
        scroll_frame._bind_mousewheel_recursive(container)

    def load_category(self, category):
        """Load category instantly (0ms) and start quiz"""
        self.current_category = category
        self.index = 0
        self.score = 0
        self.selected.set("")
        self.user_answers = []
        
        # Fetch questions instantly from data_loader
        self.questions = data_loader.fetch_questions(category)
        self.num_questions = len(self.questions)
        
        if self.num_questions == 0:
            messagebox.showerror("Error", "No questions available for this category.")
            self.show_category_selection()
            return
        
        self.build_ui()
        self.load_question()

    def build_ui(self):
        """Build the main quiz UI inside a scrollable container"""
        self.clear_root()
        
        self.scroll_frame = ScrollableFrame(self.root, bg_color=UI_SETTINGS["bg_primary"])
        self.scroll_frame.pack(fill="both", expand=True)
        container = self.scroll_frame.content

        # Header Frame
        header_frame = tk.Frame(container, bg=UI_SETTINGS["bg_header"], pady=15)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="🎓 Smart Quiz Generator",
            font=("Segoe UI", 22, "bold"),
            bg=UI_SETTINGS["bg_header"],
            fg=UI_SETTINGS["color_accent"]
        ).pack()

        cat_title = f"Category: {self.current_category.capitalize()}"
        tk.Label(
            header_frame,
            text=cat_title,
            font=("Segoe UI", 11, "italic"),
            bg=UI_SETTINGS["bg_header"],
            fg="#bbbbbb"
        ).pack(pady=2)

        # Progress Frame
        progress_frame = tk.Frame(container, bg=UI_SETTINGS["bg_secondary"], pady=8)
        progress_frame.pack(fill="x", padx=20, pady=10)

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=UI_SETTINGS["bg_secondary"],
            fg=UI_SETTINGS["color_accent"]
        )
        self.progress_label.pack()

        # Main Quiz Card Frame
        quiz_card = tk.Frame(container, bg=UI_SETTINGS["bg_secondary"], padx=25, pady=20)
        quiz_card.pack(fill="both", expand=True, padx=20, pady=10)

        # Question Label
        self.q_label = tk.Label(
            quiz_card,
            text="",
            wraplength=700,
            font=("Segoe UI", 15, "bold"),
            bg=UI_SETTINGS["bg_secondary"],
            fg="#ffffff",
            justify="left",
            anchor="w"
        )
        self.q_label.pack(fill="x", pady=(0, 15))

        # Options Container
        self.options_box = tk.Frame(quiz_card, bg=UI_SETTINGS["bg_secondary"])
        self.options_box.pack(fill="x", pady=10)

        self.radio_buttons = []
        self.option_frames = []

        for i in range(4):
            opt_frame = tk.Frame(self.options_box, bg=UI_SETTINGS["bg_primary"], bd=1, relief="solid")
            opt_frame.pack(fill="x", pady=6)
            opt_frame.config(highlightthickness=1, highlightbackground=UI_SETTINGS["color_accent"])

            rb = tk.Radiobutton(
                opt_frame,
                text="",
                variable=self.selected,
                value="",
                font=("Segoe UI", 12),
                bg=UI_SETTINGS["bg_primary"],
                fg="#ffffff",
                activebackground=UI_SETTINGS["color_accent"],
                activeforeground=UI_SETTINGS["bg_primary"],
                selectcolor=UI_SETTINGS["bg_secondary"],
                anchor="w",
                justify="left",
                padx=15,
                pady=12,
                cursor="hand2"
            )
            rb.pack(fill="x", anchor="w")
            self.radio_buttons.append(rb)
            self.option_frames.append(opt_frame)

        # Feedback Area
        self.feedback = tk.Label(
            quiz_card,
            text="",
            wraplength=700,
            font=("Segoe UI", 12),
            bg=UI_SETTINGS["bg_secondary"],
            fg="#ffffff",
            justify="left"
        )
        self.feedback.pack(fill="x", pady=12)

        # Action Buttons Frame
        btn_frame = tk.Frame(container, bg=UI_SETTINGS["bg_primary"], pady=15)
        btn_frame.pack(fill="x", padx=20)

        self.submit_btn = tk.Button(
            btn_frame,
            text="Submit Answer",
            command=self.check_answer,
            bg=UI_SETTINGS["color_accent"],
            fg=UI_SETTINGS["bg_primary"],
            font=("Segoe UI", 12, "bold"),
            padx=25,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        self.submit_btn.pack(side="left", padx=10)

        self.next_btn = tk.Button(
            btn_frame,
            text="Next Question →",
            command=self.next_question,
            bg="#28a745",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            padx=25,
            pady=10,
            relief="flat",
            state="disabled",
            cursor="hand2"
        )
        self.next_btn.pack(side="left", padx=10)

        self.change_cat_btn = tk.Button(
            btn_frame,
            text="← Categories",
            command=self.show_category_selection,
            bg=UI_SETTINGS["bg_secondary"],
            fg="#cccccc",
            font=("Segoe UI", 11),
            padx=15,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        self.change_cat_btn.pack(side="right", padx=10)

        self.scroll_frame._bind_mousewheel_recursive(container)

    def load_question(self):
        """Load current question onto the UI"""
        self.selected.set("")
        self.feedback.config(text="", fg="#ffffff")
        self.next_btn.config(state="disabled")
        self.submit_btn.config(state="normal")

        for frame in self.option_frames:
            frame.config(highlightbackground=UI_SETTINGS["color_accent"])

        q = self.questions[self.index]

        self.progress_label.config(
            text=f"Question {self.index + 1} of {self.num_questions}"
        )

        self.q_label.config(text=f"Q{self.index + 1}. {q['question']}")

        options = list(q["options"])
        random.shuffle(options)

        # Handle questions that might have fewer/more than 4 options gracefully
        for i in range(4):
            if i < len(options):
                opt = options[i]
                self.radio_buttons[i].config(text=opt, value=opt, state="normal")
                self.option_frames[i].pack(fill="x", pady=6)
            else:
                self.option_frames[i].pack_forget()

        # Update scroll region
        self.root.update_idletasks()
        self.scroll_frame.canvas.configure(scrollregion=self.scroll_frame.canvas.bbox("all"))
        self.scroll_frame.canvas.yview_moveto(0)

    def check_answer(self):
        """Check selected answer and display feedback"""
        if not self.selected.get():
            messagebox.showwarning("Warning", "Please select an answer option!")
            return

        q = self.questions[self.index]
        user_answer = self.selected.get()
        is_correct = (user_answer == q["answer"])

        self.user_answers.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

        if is_correct:
            self.score += 1
            self.feedback.config(
                text="✅ Correct!\n" + q.get("explanation", ""),
                fg="#00ff00"
            )
        else:
            self.feedback.config(
                text=f"❌ Wrong!\nCorrect Answer: {q['answer']}\n{q.get('explanation', '')}",
                fg="#ff6b6b"
            )

        self.next_btn.config(state="normal")
        self.submit_btn.config(state="disabled")
        
        # Auto scroll down to feedback if needed
        self.root.update_idletasks()
        self.scroll_frame.canvas.configure(scrollregion=self.scroll_frame.canvas.bbox("all"))

    def next_question(self):
        """Advance to next question or show results"""
        self.index += 1
        if self.index < len(self.questions):
            self.load_question()
        else:
            self.show_result()

    def show_result(self):
        """Display quiz summary with full scrollability"""
        self.clear_root()

        scroll_frame = ScrollableFrame(self.root, bg_color=UI_SETTINGS["bg_primary"])
        scroll_frame.pack(fill="both", expand=True)
        container = scroll_frame.content

        # Header
        header_frame = tk.Frame(container, bg=UI_SETTINGS["bg_header"], pady=20)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="🎉 Quiz Completed!",
            font=("Segoe UI", 24, "bold"),
            bg=UI_SETTINGS["bg_header"],
            fg=UI_SETTINGS["color_accent"]
        ).pack()

        # Score Card
        score_card = tk.Frame(container, bg=UI_SETTINGS["bg_secondary"], padx=20, pady=15)
        score_card.pack(fill="x", padx=20, pady=15)

        percentage = (self.score / self.num_questions) * 100 if self.num_questions > 0 else 0
        grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 70 else "C" if percentage >= 60 else "D"

        score_text = f"Score: {self.score}/{self.num_questions}  ({percentage:.1f}%)   |   Grade: {grade}"
        tk.Label(
            score_card,
            text=score_text,
            font=("Segoe UI", 16, "bold"),
            bg=UI_SETTINGS["bg_secondary"],
            fg=UI_SETTINGS["color_accent"]
        ).pack(pady=5)

        # Review Header
        tk.Label(
            container,
            text="📋 Detailed Review",
            font=("Segoe UI", 16, "bold"),
            bg=UI_SETTINGS["bg_primary"],
            fg="#ffffff",
            anchor="w"
        ).pack(fill="x", padx=25, pady=(15, 5))

        # Detailed Question Breakdown Cards
        for idx, answer in enumerate(self.user_answers, 1):
            card_bg = "#1a3a2a" if answer["is_correct"] else "#3a1a1a"
            card_border = "#00ff00" if answer["is_correct"] else "#ff6b6b"
            
            ans_card = tk.Frame(container, bg=card_bg, bd=1, relief="solid", padx=15, pady=12)
            ans_card.pack(fill="x", padx=20, pady=8)
            ans_card.config(highlightthickness=1, highlightbackground=card_border)

            status_icon = "✅ CORRECT" if answer["is_correct"] else "❌ INCORRECT"
            
            tk.Label(
                ans_card,
                text=f"Q{idx}. {answer['question']}",
                font=("Segoe UI", 12, "bold"),
                bg=card_bg,
                fg="#ffffff",
                wraplength=650,
                justify="left"
            ).pack(anchor="w", pady=(0, 4))

            tk.Label(
                ans_card,
                text=f"Result: {status_icon}",
                font=("Segoe UI", 11, "bold"),
                bg=card_bg,
                fg="#00ff00" if answer["is_correct"] else "#ff6b6b"
            ).pack(anchor="w")

            tk.Label(
                ans_card,
                text=f"Your Answer: {answer['user_answer']}",
                font=("Segoe UI", 11),
                bg=card_bg,
                fg="#ffffff"
            ).pack(anchor="w")

            if not answer["is_correct"]:
                tk.Label(
                    ans_card,
                    text=f"Correct Answer: {answer['correct_answer']}",
                    font=("Segoe UI", 11, "bold"),
                    bg=card_bg,
                    fg="#00d4ff"
                ).pack(anchor="w")

            if answer.get("explanation"):
                tk.Label(
                    ans_card,
                    text=f"Explanation: {answer['explanation']}",
                    font=("Segoe UI", 10, "italic"),
                    bg=card_bg,
                    fg="#cccccc",
                    wraplength=650,
                    justify="left"
                ).pack(anchor="w", pady=(4, 0))

        # Bottom Action Buttons
        btn_frame = tk.Frame(container, bg=UI_SETTINGS["bg_primary"], pady=20)
        btn_frame.pack(fill="x")

        restart_btn = tk.Button(
            btn_frame,
            text="Try Another Category",
            command=self.show_category_selection,
            bg=UI_SETTINGS["color_accent"],
            fg=UI_SETTINGS["bg_primary"],
            font=("Segoe UI", 12, "bold"),
            padx=25,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        restart_btn.pack(side="left", padx=20)

        exit_btn = tk.Button(
            btn_frame,
            text="Exit App",
            command=self.root.quit,
            bg="#ff6b6b",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            padx=25,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        exit_btn.pack(side="left", padx=10)

        scroll_frame._bind_mousewheel_recursive(container)


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
