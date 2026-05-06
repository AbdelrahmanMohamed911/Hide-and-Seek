import customtkinter as ctk
from tkinter import messagebox
from src.game.services import get_input, generate_random_places, create_payoff_matrix, computer_move
from src.solver.computer_solver import solve
from src.game.game_engine import GameEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

type_map = {
    "neutral": "Neutral",
    "easy_for_seeker": "Easy",
    "hard_for_seeker": "Hard"
}

class PayoffGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.stage = "INPUT"
        self.selected_place = None
        self.selected_role = None

        self.title("HIDE & SEEK: STRATEGY ENGINE")
        self.geometry("600x650")
        self.configure(fg_color="#111111")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.header_label = ctk.CTkLabel(
            self, 
            text="MISSION PARAMETERS", 
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
            text_color="#2ecc71"  
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=2, border_color="#2ecc71")
        self.input_frame.grid(row=1, column=0, padx=30, pady=8, sticky="ew")
        self.input_frame.grid_columnconfigure((0, 1), weight=1)

        self.label_n = ctk.CTkLabel(self.input_frame, text="WORLD SIZE (N):", font=("Courier", 14))
        self.label_n.grid(row=0, column=0, columnspan=2, pady=(14, 4))
        
        self.entry_n = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Enter N...", 
            width=200, 
            fg_color="#000000", 
            border_color="#3498db"
        )
        self.entry_n.grid(row=1, column=0, columnspan=2, pady=(0, 6))
        self.entry_n.insert(0, "4")

        self.check_1d = ctk.CTkCheckBox(self.input_frame, text="1D DIMENSION", text_color="#3498db", font=("Courier", 12))
        self.check_1d.select()
        self.check_1d.grid(row=2, column=0, padx=30, pady=12, sticky="w")

        self.check_proximity = ctk.CTkCheckBox(self.input_frame, text="PROXIMITY RADAR", text_color="#3498db", font=("Courier", 12))
        self.check_proximity.grid(row=2, column=1, padx=30, pady=12, sticky="e")

        self.btn_generate = ctk.CTkButton(
            self.input_frame, 
            text="INITIALIZE PAYOFF MATRIX", 
            command=self.run_logic,
            font=("Courier", 16, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45
        )
        self.btn_generate.grid(row=3, column=0, columnspan=2, sticky="ew", padx=0, pady=0)

        self.console_label = ctk.CTkLabel(self, text="SYSTEM DATA OUTPUT:", font=("Courier", 12), text_color="#95a5a6")
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")

        # Game Frame (initially hidden)
        self.game_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=2, border_color="#2ecc71")
        self.game_frame.grid(row=1, column=0, padx=30, pady=8, sticky="ew")
        self.game_frame.grid_remove()

        # Game scoreboard
        self.score_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.score_frame.grid(row=2, column=0, padx=30, pady=(0, 6), sticky="ew")
        self.score_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.score_frame.grid_remove()

        self._score_vals = {}
        for col, (key, lbl) in enumerate([
            ("your_score", "YOUR SCORE"),
            ("computer_score", "COMPUTER SCORE"),
            ("rounds_won", "ROUNDS WON"),
            ("rounds_lost", "ROUNDS LOST"),
        ]):
            card = ctk.CTkFrame(self.score_frame, fg_color="#0a0a0a", border_width=1, border_color="#333333", corner_radius=6)
            card.grid(row=0, column=col, padx=4, sticky="ew")
            num = ctk.CTkLabel(card, text="0", font=("Courier", 20, "bold"), text_color="#2ecc71")
            num.pack(pady=(8, 0))
            ctk.CTkLabel(card, text=lbl, font=("Courier", 10), text_color="#555555").pack(pady=(0, 8))
            self._score_vals[key] = num
        
        self.output_text = ctk.CTkTextbox(
            self, 
            fg_color="#000000", 
            text_color="#2ecc71", 
            font=("Consolas", 12),
            border_width=1,
            border_color="#2ecc71"
        )
        self.output_text.grid(row=5, column=0, padx=30, pady=(0, 30), sticky="nsew")

    def run_logic(self):
        try:
            n_val = self.entry_n.get()
            is_1d = self.check_1d.get()
            prox = self.check_proximity.get()
            
            input_m = get_input(n_val, is_1d, prox)
            
            if not input_m:
                messagebox.showerror("TERMINAL ERROR", "Invalid World Size Detected.")
                return

            self.world_m = generate_random_places(input_m)
            self.payoff_m = create_payoff_matrix(self.world_m)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", f"> WORLD GENERATED: {self.world_m.places_hardness}\n")
            self.output_text.insert("end", "> CALIBRATING PAYOFFS...\n")
            self.output_text.insert("end", "> MATRIX READY:\n\n")
            self.output_text.insert("end", str(self.payoff_m.matrix))

            self.computer_probabilities_seeker, _ = solve(self.payoff_m, "hider")  
            self.computer_probabilities_hider, _ = solve(self.payoff_m, "seeker")
            # print("Computer Probabilities (Seeker):", self.computer_probabilities_seeker)
            # print("Computer Probabilities (Hider):", self.computer_probabilities_hider)
            self.output_text.insert("end", "\n\n> OPTIMAL COMPUTER STRATEGY CALCULATED(Human Role: HIDER)\n\n")
            self.output_text.insert("end", str(self.computer_probabilities_seeker.tolist()))
            self.output_text.insert("end", "\n\n> OPTIMAL COMPUTER STRATEGY CALCULATED(Human Role: SEEKER)\n\n")
            self.output_text.insert("end", str(self.computer_probabilities_hider.tolist()))
            self.game_engine = GameEngine(self.payoff_m)

            self.set_stage("GAME")

        except Exception as e:
            messagebox.showerror("SYSTEM CRITICAL", f"Error: {str(e)}")

    def set_stage(self, new_stage):
        self.stage = new_stage

        self.input_frame.grid_remove()
        self.game_frame.grid_remove()
        self.score_frame.grid_remove()

        if new_stage == "INPUT":
            self.header_label.configure(text="MISSION PARAMETERS")
            self.input_frame.grid()
            self.game_engine.reset_scoreboard()
            self.update_scores(0, 0, 0, 0)
            self.selected_place = None
            self.selected_role  = None

        elif new_stage == "GAME":
            self.header_label.configure(text="HIDE & SEEK — CHOOSE ROLE & PLACE")
            self.game_frame.grid()
            self.score_frame.grid()
            self.setup_game()


    def setup_game(self):
        # clear previous role buttons
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # make all place columns equal weight
        N = len(self.world_m.places_hardness)
        for c in range(N):
            self.game_frame.grid_columnconfigure(c, weight=1)

        place_lavbel = ctk.CTkLabel(self.game_frame,text="SELECT YOUR PLACE:",font=("Courier", 11),text_color="#555555")
        place_lavbel.grid(row=0, column=0, columnspan=N, padx=10, pady=(12, 4), sticky="w")

        
        for i, place_type in enumerate(self.world_m.places_hardness):
            btn = ctk.CTkButton(
                self.game_frame,
                text=f"P{i+1}\n{type_map.get(place_type, place_type)}",
                command=lambda i=i: self.on_select_place(i),
                font=("Courier", 12, "bold"),
                fg_color="#0a0a0a",
                border_width=2,
                border_color="#2ecc71",
                text_color="#2ecc71",
                hover_color="#2ecc71",
                height=58,
                corner_radius=6
            )
            btn.grid(row=1, column=i, padx=5, pady=(0, 8), sticky="ew")

        role_label = ctk.CTkLabel(self.game_frame, text="SELECT YOUR ROLE:", font=("Courier", 11), text_color="#555555")
        role_label.grid(row=2, column=0, columnspan=N, padx=10, pady=(4, 4), sticky="w")

        col_mid = N // 2
        ctk.CTkButton(
            self.game_frame,
            text="HIDER",
            command=lambda: self.on_select_role("HIDER"),
            font=("Courier", 13, "bold"),
            fg_color="transparent",
            border_width=2,
            border_color="#3498db",
            text_color="#3498db",
            hover_color="#1a3a5a",
            height=40,
            corner_radius=6
        ).grid(row=3, column=0, columnspan=col_mid, padx=5, pady=(0, 8), sticky="ew")

        ctk.CTkButton(
            self.game_frame,
            text="SEEKER",
            command=lambda: self.on_select_role("SEEKER"),
            font=("Courier", 13, "bold"),
            fg_color="transparent",
            border_width=2,
            border_color="#3498db",
            text_color="#3498db",
            hover_color="#1a3a5a",
            height=40,
            corner_radius=6
        ).grid(row=3, column=col_mid, columnspan=N - col_mid, padx=5, pady=(0, 8), sticky="ew")

        ctk.CTkButton(
            self.game_frame, text="PLAY ROUND",
            command=self.run_game,
            font=("Courier", 13, "bold"),
            fg_color="#27ae60",
            hover_color="#1e8449",
            height=40,
            corner_radius=6
        ).grid(row=4, column=0, columnspan=col_mid, padx=5, pady=(4, 4), sticky="ew")

        ctk.CTkButton(
            self.game_frame, text="SIMULATE",
            command=self.simulate,
            font=("Courier", 13, "bold"),
            fg_color="transparent",
            border_width=2,
            border_color="#3498db",
            text_color="#3498db",
            hover_color="#1a3a5a",
            height=40,
            corner_radius=6
        ).grid(row=4, column=col_mid, columnspan=N - col_mid, padx=5, pady=(4, 4), sticky="ew")

        ctk.CTkButton(
            self.game_frame, text="RESET",
            command=lambda: self.set_stage("INPUT"),
            font=("Courier", 13, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=38,
            corner_radius=6
        ).grid(row=5, column=0, columnspan=N, padx=5, pady=(0, 10), sticky="ew")


    def on_select_place(self, index):
        self.selected_place = index
        # highlight selected place
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text").startswith(f"P{index+1}"):
                widget.configure(border_color="#e67e22")
            elif isinstance(widget, ctk.CTkButton) and widget.cget("text").startswith("P"):
                widget.configure(border_color="#2ecc71")

    def on_select_role(self, role):
        self.game_engine.human_role = role.lower()
        self.selected_role = role.lower()
        # highlight selected role
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == role:
                widget.configure(border_color="#e67e22")
            elif isinstance(widget, ctk.CTkButton) and widget.cget("text") in ["HIDER", "SEEKER"]:
                widget.configure(border_color="#3498db")

    def run_game(self):
        if self.selected_place is None or self.selected_role is None:
            messagebox.showwarning("INCOMPLETE SELECTION", "Please select both a place and a role before playing.")
            return
        
        computer_position = None
        if self.selected_role == "hider":
            computer_position = computer_move(self.computer_probabilities_seeker)
        else:
            computer_position = computer_move(self.computer_probabilities_hider)

        print(f"Computer chose position: {computer_position}")
        print(f"Human chose position: {self.selected_place}")
        self.game_engine.play_round(self.selected_place, computer_position)

        # Update scores on the GUI
        self.update_scores(
            your_score=self.game_engine.human_total_score,
            computer_score=self.game_engine.computer_total_score,
            won=self.game_engine.human_rounds_won,
            lost=self.game_engine.computer_rounds_won
        )

    def update_scores(self, your_score, computer_score, won, lost):
        self.output_text.configure(text_color="#2ecc71")
        self._score_vals["your_score"].configure(text=str(your_score))
        self._score_vals["computer_score"].configure(text=str(computer_score))
        self._score_vals["rounds_won"].configure(text=str(won))
        self._score_vals["rounds_lost"].configure(text=str(lost))

    def simulate(self):
        self.game_engine.reset_scoreboard()
        self.game_engine.play_simulation()
        self.update_scores(
            your_score=self.game_engine.human_total_score,
            computer_score=self.game_engine.computer_total_score,
            won=self.game_engine.human_rounds_won,
            lost=self.game_engine.computer_rounds_won
        )