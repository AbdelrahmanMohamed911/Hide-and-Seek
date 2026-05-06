import customtkinter as ctk
from tkinter import messagebox
from src.game.services import get_input, generate_random_places, create_payoff_matrix, computer_move, get_1D_index
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

        self.stage          = "INPUT"
        self.selected_place = None
        self.selected_role  = None
        self.place_buttons  = {}
        self.role_buttons   = {}
        self.game_engine    = None

        self.title("HIDE & SEEK: STRATEGY ENGINE")
        self.geometry("620x700")
        self.configure(fg_color="#111111")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self, 
            text="MISSION PARAMETERS", 
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
            text_color="#2ecc71"  
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(28, 8))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=1, border_color="#555555")
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
            text="START GAME", 
            command=self.run_logic,
            font=("Courier", 16, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=45
        )
        self.btn_generate.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        self.console_label = ctk.CTkLabel(self, text="SYSTEM DATA OUTPUT:", font=("Courier", 12), text_color="#95a5a6")
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")

        # Game Frame (initially hidden)
        self.game_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=1, border_color="#555555")
        self.game_frame.grid(row=1, column=0, padx=30, pady=8, sticky="ew")
        self.game_frame.grid_remove()

        # SCORE FRAME (hidden until GAME stage) 
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

        # CONSOLE LABEL
        self.console_label = ctk.CTkLabel(
            self, text="SYSTEM DATA OUTPUT:",
            font=("Courier", 12), text_color="#95a5a6"
        )
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")

        # OUTPUT TEXTBOX
        self.output_text = ctk.CTkTextbox(
            self, 
            fg_color="#000000", 
            text_color="#2ecc71", 
            font=("Consolas", 12),
            border_width=1,
            border_color="#555555"
        )
        self.output_text.grid(row=5, column=0, padx=30, pady=(0, 28), sticky="nsew")


    def run_logic(self):
        try:
            n_val = self.entry_n.get()
            is_1d = self.check_1d.get()
            prox  = self.check_proximity.get()

            self.input_m = get_input(n_val, is_1d, prox)
            if not self.input_m:
                messagebox.showerror("TERMINAL ERROR", "Invalid World Size Detected.")
                return

            self.world_m  = generate_random_places(self.input_m)
            self.payoff_m = create_payoff_matrix(self.world_m)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", f"> WORLD GENERATED: {self.world_m.places_hardness}\n")
            self.output_text.insert("end", "> CALIBRATING PAYOFFS...\n")
            self.output_text.insert("end", "> MATRIX READY:\n\n")
            self.output_text.insert("end", str(self.payoff_m.matrix))

            self.computer_probabilities_seeker, _ = solve(self.payoff_m, "hider")
            self.computer_probabilities_hider, _  = solve(self.payoff_m, "seeker")

            self.output_text.insert("end", "\n\n> OPTIMAL COMPUTER STRATEGY CALCULATED(Human Role: HIDER)\n\n")
            self.output_text.insert("end", str(self.computer_probabilities_seeker.tolist()))
            self.output_text.insert("end", "\n\n> OPTIMAL COMPUTER STRATEGY CALCULATED(Human Role: SEEKER)\n\n")
            self.output_text.insert("end", str(self.computer_probabilities_hider.tolist()))

            self.game_engine = GameEngine(self.payoff_m)
            self.set_stage("GAME")

        except Exception as e:
            messagebox.showerror("SYSTEM CRITICAL", f"Error: {str(e)}")

    # STAGE SWITCHING 
    def set_stage(self, new_stage):
        self.stage = new_stage
        self.input_frame.grid_remove()
        self.game_frame.grid_remove()
        self.score_frame.grid_remove()

        if new_stage == "INPUT":
            self.header_label.configure(text="MISSION PARAMETERS")
            self.input_frame.grid()
            if self.game_engine is not None:
                self.game_engine.reset_scoreboard()
                self.update_scores(0, 0, 0, 0)
            self.selected_place = None
            self.selected_role  = None

        elif new_stage == "GAME":
            self.header_label.configure(text="HIDE & SEEK — CHOOSE ROLE & PLACE")
            self.game_frame.grid()
            self.score_frame.grid()
            self.setup_game()

    # BUILD GAME FRAME 
    def setup_game(self):
        self.place_buttons = {}
        self.role_buttons  = {}

        # clear all previous widgets
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        N = len(self.world_m.places_hardness)

        # Place label
        ctk.CTkLabel(
            self.game_frame, text="SELECT YOUR PLACE:",
            font=("Courier", 11), text_color="#555555"
        ).grid(row=0, column=0, columnspan=N, padx=10, pady=(12, 4), sticky="w")

        # Place buttons
        if not self.input_m.is_1D:
            # 2D: columns based on grid width
            for c in range(self.input_m.n):
                self.game_frame.grid_columnconfigure(c, weight=1)
            for i in range(self.input_m.n):
                for j in range(self.input_m.n):
                    place_num  = get_1D_index(self.input_m, i, j)
                    place_type = self.world_m.places_hardness[place_num]
                    btn = ctk.CTkButton(
                        self.game_frame,
                        text=f"P{place_num+1}\n{type_map.get(place_type, place_type)}",
                        command=lambda p=place_num: self.on_select_place(p),
                        font=("Courier", 12, "bold"),
                        fg_color="#0a0a0a",
                        border_width=2,
                        border_color="#2ecc71",
                        text_color="#2ecc71",
                        hover_color="#1a6b3a",
                        height=58,
                        corner_radius=6
                    )
                    # row+1 to leave row=0 for the label
                    btn.grid(row=i + 1, column=j, padx=5, pady=(0, 8), sticky="ew")
                    self.place_buttons[place_num] = btn
            place_rows = self.input_m.n
        else:
            # 1D: single row of buttons
            for c in range(N):
                self.game_frame.grid_columnconfigure(c, weight=1)
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
                    hover_color="#1a6b3a",
                    height=58,
                    corner_radius=6
                )
                btn.grid(row=1, column=i, padx=5, pady=(0, 8), sticky="ew")
                self.place_buttons[i] = btn
            place_rows = 1

        # base row — everything below place buttons uses this offset
        base = place_rows + 1

        col_mid = N // 2

        # Role label
        ctk.CTkLabel(
            self.game_frame, text="SELECT YOUR ROLE:",
            font=("Courier", 11), text_color="#555555"
        ).grid(row=base, column=0, columnspan=N, padx=10, pady=(4, 4), sticky="w")

        # Role buttons — stored as refs so we can recolor without scanning widgets
        hider_btn = ctk.CTkButton(
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
        )
        hider_btn.grid(row=base + 1, column=0, columnspan=col_mid, padx=5, pady=(0, 8), sticky="ew")

        seeker_btn = ctk.CTkButton(
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
        )
        seeker_btn.grid(row=base + 1, column=col_mid, columnspan=N - col_mid, padx=5, pady=(0, 8), sticky="ew")

        self.role_buttons = {"HIDER": hider_btn, "SEEKER": seeker_btn}

        # Action buttons
        ctk.CTkButton(
            self.game_frame, text="▶  PLAY ROUND",
            command=self.run_game,
            font=("Courier", 14, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=45,
            corner_radius=6
        ).grid(row=base + 2, column=0, columnspan=N, padx=5, pady=(4, 4), sticky="ew")

        ctk.CTkButton(
            self.game_frame, text="⚡  SIMULATE",
            command=self.simulate,
            font=("Courier", 11, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=34,
            corner_radius=6
        ).grid(row=base + 3, column=0, columnspan=col_mid, padx=5, pady=(0, 8), sticky="ew")

        ctk.CTkButton(
            self.game_frame, text="↺  RESET",
            command=lambda: self.set_stage("INPUT"),
            font=("Courier", 11, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=34,
            corner_radius=6
        ).grid(row=base + 3, column=col_mid, columnspan=N - col_mid, padx=5, pady=(0, 8), sticky="ew")

    # SELECTION HANDLERS 

    def on_select_place(self, index):
        self.selected_place = index
        for place_num, btn in self.place_buttons.items():
            if place_num == index:
                btn.configure(border_color="#e67e22")
            else:
                btn.configure(border_color="#2ecc71")

    def on_select_role(self, role):
        self.game_engine.human_role = role.lower()
        self.selected_role = role.lower()
        # use stored refs — no widget scanning needed
        for r, btn in self.role_buttons.items():
            if r == role:
                btn.configure(fg_color="#3498db", text_color="#000000")
            else:
                btn.configure(fg_color="transparent", text_color="#3498db")

    # GAME ACTIONS

    def run_game(self):
        if self.selected_place is None or self.selected_role is None:
            messagebox.showwarning("INCOMPLETE SELECTION", "Please select both a place and a role before playing.")
            return

        if self.selected_role == "hider":
            computer_position = computer_move(self.computer_probabilities_seeker)
        else:
            computer_position = computer_move(self.computer_probabilities_hider)

        print(f"Computer chose position: {computer_position}")
        print(f"Human chose position: {self.selected_place}")
        self.game_engine.play_round(self.selected_place, computer_position)

        self.update_scores(
            your_score=self.game_engine.human_total_score,
            computer_score=self.game_engine.computer_total_score,
            won=self.game_engine.human_rounds_won,
            lost=self.game_engine.computer_rounds_won
        )

    def simulate(self):
        self.game_engine.reset_scoreboard()
        self.game_engine.play_simulation()
        self.update_scores(
            your_score=self.game_engine.human_total_score,
            computer_score=self.game_engine.computer_total_score,
            won=self.game_engine.human_rounds_won,
            lost=self.game_engine.computer_rounds_won
        )

    def update_scores(self, your_score, computer_score, won, lost):
        self._score_vals["your_score"].configure(text=str(your_score))
        self._score_vals["computer_score"].configure(text=str(computer_score))
        self._score_vals["rounds_won"].configure(text=str(won))
        self._score_vals["rounds_lost"].configure(text=str(lost))