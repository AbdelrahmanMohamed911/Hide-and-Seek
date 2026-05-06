import customtkinter as ctk
from tkinter import messagebox
from src.game.services import get_input, generate_random_places, create_payoff_matrix, computer_move, get_1D_index
from src.solver.computer_solver import solve
from src.game.game_engine import GameEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

type_map = {
    "neutral":         "⚠️(Neutral)",   # moderate — warning
    "easy_for_seeker": "💀(Easy)",   # dangerous for hider — skull
    "hard_for_seeker": "🛡️(Hard)",  # safe for hider — shield
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
        self.grid_rowconfigure(0, weight=1)
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="#111111")
        self._scroll.grid(row=0, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)
        self._scroll.grid_rowconfigure(5, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self._scroll, 
            text="MISSION PARAMETERS", 
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
            text_color="#2ecc71"  
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(28, 8))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self._scroll, fg_color="#1a1a1a", border_width=1, border_color="#555555")
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

        self.console_label = ctk.CTkLabel(self._scroll, text="SYSTEM DATA OUTPUT:", font=("Courier", 12), text_color="#95a5a6")
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")

        # Game Frame (initially hidden)
        self.game_frame = ctk.CTkFrame(self._scroll, fg_color="#1a1a1a", border_width=1, border_color="#555555")
        self.game_frame.grid(row=1, column=0, padx=30, pady=8, sticky="ew")
        self.game_frame.grid_remove()

        # SCORE FRAME (hidden until GAME stage) 
        self.score_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
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
            self._scroll, text="SYSTEM DATA OUTPUT:",
            font=("Courier", 12), text_color="#95a5a6"
        )
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")

        # OUTPUT TEXTBOX
        self.output_text = ctk.CTkTextbox(
            self._scroll,
            fg_color="#000000",
            text_color="#2ecc71",
            font=("Consolas", 12),
            border_width=1,
            border_color="#555555",
            wrap="none",          
        )
        self.output_text.grid(row=5, column=0, padx=30, pady=(0, 28), sticky="nsew")


    def _format_matrix(self, matrix):
        import numpy as np
        arr = np.array(matrix)
        rows, cols = arr.shape
        col_w = max(len(f"{v:.3f}") for v in arr.flat)
        col_w = max(col_w, 5)
        header = "      " + "  ".join(f"S{j+1}".ljust(col_w) for j in range(cols))
        sep    = "      " + "  ".join("-" * col_w for _ in range(cols))
        lines  = [header, sep]
        for i, row in enumerate(arr):
            cells = "  ".join(f"{v:{col_w}.3f}" for v in row)
            lines.append(f"  H{i+1} | {cells}")
        return "\n".join(lines)

    def _format_probs(self, probs):
        import numpy as np
        arr = np.array(probs).flatten()
        entries = [f"P{i+1}: {v:.4f}" for i, v in enumerate(arr)]
        chunk = 4
        lines = []
        for start in range(0, len(entries), chunk):
            lines.append("  ".join(entries[start:start+chunk]))
        return "\n".join(lines)

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

            self.computer_probabilities_seeker, _ = solve(self.payoff_m, "hider")
            self.computer_probabilities_hider, _  = solve(self.payoff_m, "seeker")

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", f"> WORLD GENERATED:\n  {self.world_m.places_hardness}\n\n")
            self.output_text.insert("end", "> CALIBRATING PAYOFFS...\n")
            self.output_text.insert("end", "> PAYOFF MATRIX  (rows = Hider place, cols = Seeker place):\n\n")
            self.output_text.insert("end", self._format_matrix(self.payoff_m.matrix))
            self.output_text.insert("end", "\n\n> COMPUTER STRATEGY — Human plays HIDER  (comp is seeker):\n\n")
            self.output_text.insert("end", self._format_probs(self.computer_probabilities_seeker))
            self.output_text.insert("end", "\n\n> COMPUTER STRATEGY — Human plays SEEKER  (comp is hider):\n\n")
            self.output_text.insert("end", self._format_probs(self.computer_probabilities_hider))

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

        self.game_frame.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=10, pady=(12, 2), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top_bar, text="SELECT YOUR PLACE:",
            font=("Courier", 11), text_color="#555555"
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            top_bar,
            text="🛡️ Safe  ⚠️ Neutral  💀 Danger",
            font=("Courier", 10), text_color="#666666"
        ).grid(row=0, column=1, sticky="e")

        BTN_W = 80  

        if not self.input_m.is_1D:
            for i in range(self.input_m.n):
                row_scroll = ctk.CTkScrollableFrame(
                    self.game_frame, orientation="horizontal",
                    fg_color="transparent", height=74
                )
                row_scroll.grid(row=i + 1, column=0, padx=6, pady=(0, 4), sticky="ew")
                for j in range(self.input_m.n):
                    place_num  = get_1D_index(self.input_m, i, j)
                    place_type = self.world_m.places_hardness[place_num]
                    btn = ctk.CTkButton(
                        row_scroll,
                        text=f"P{place_num+1}\n{type_map.get(place_type, place_type)}",
                        command=lambda p=place_num: self.on_select_place(p),
                        font=("Courier", 14, "bold"),
                        fg_color="#0a0a0a",
                        border_width=2,
                        border_color="#2ecc71",
                        text_color="#2ecc71",
                        hover_color="#1a6b3a",
                        width=BTN_W,
                        height=58,
                        corner_radius=6
                    )
                    btn.grid(row=0, column=j, padx=5, pady=4)
                    self.place_buttons[place_num] = btn
            place_rows = self.input_m.n
        else:
            h_scroll = ctk.CTkScrollableFrame(
                self.game_frame, orientation="horizontal",
                fg_color="transparent", height=74
            )
            h_scroll.grid(row=1, column=0, padx=6, pady=(0, 4), sticky="ew")
            for i, place_type in enumerate(self.world_m.places_hardness):
                btn = ctk.CTkButton(
                    h_scroll,
                    text=f"P{i+1}\n{type_map.get(place_type, place_type)}",
                    command=lambda i=i: self.on_select_place(i),
                    font=("Courier", 14, "bold"),
                    fg_color="#0a0a0a",
                    border_width=2,
                    border_color="#2ecc71",
                    text_color="#2ecc71",
                    hover_color="#1a6b3a",
                    width=BTN_W,
                    height=58,
                    corner_radius=6
                )
                btn.grid(row=0, column=i, padx=5, pady=4)
                self.place_buttons[i] = btn
            place_rows = 1

        # base row — everything below place buttons uses this offset
        base = place_rows + 1

        col_mid = 1  
        self.game_frame.grid_columnconfigure(0, weight=1)

        # Role label
        ctk.CTkLabel(
            self.game_frame, text="SELECT YOUR ROLE:",
            font=("Courier", 11), text_color="#555555"
        ).grid(row=base, column=0, padx=10, pady=(4, 4), sticky="w")

        role_row = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        role_row.grid(row=base + 1, column=0, padx=5, pady=(0, 8), sticky="ew")
        role_row.grid_columnconfigure((0, 1), weight=1)

        hider_btn = ctk.CTkButton(
            role_row,
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
        hider_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        seeker_btn = ctk.CTkButton(
            role_row,
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
        seeker_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

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
        ).grid(row=base + 2, column=0, padx=5, pady=(4, 4), sticky="ew")

        sim_reset_row = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        sim_reset_row.grid(row=base + 3, column=0, padx=5, pady=(0, 8), sticky="ew")
        sim_reset_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            sim_reset_row, text="⚡  SIMULATE",
            command=self.simulate,
            font=("Courier", 11, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=34,
            corner_radius=6
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkButton(
            sim_reset_row, text="↺  RESET",
            command=lambda: self.set_stage("INPUT"),
            font=("Courier", 11, "bold"),
            fg_color="#0d0d0d",
            hover_color="#222222",
            border_width=1,
            border_color="#555555",
            text_color="#ffffff",
            height=34,
            corner_radius=6
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

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

    def highlight_round(self, hider_pos, seeker_pos, human_role):
        hider_label  = "HIDER\n(YOU)" if human_role == "hider" else "HIDER\n(COMP)"
        seeker_label = "SEEKER\n(YOU)" if human_role == "seeker" else "SEEKER\n(COMP)"

        for place_num, btn in self.place_buttons.items():
            place_type = self.world_m.places_hardness[place_num]
            base_text  = f"P{place_num+1}\n{type_map.get(place_type, place_type)}"

            if place_num == hider_pos and place_num == seeker_pos:
                btn.configure(
                    border_color="#e74c3c",
                    fg_color="#3d0000",
                    text_color="#ffffff",
                    text=f"{base_text}\n{hider_label} & {seeker_label}"
                )
            elif place_num == hider_pos:
                btn.configure(
                    border_color="#3498db",
                    fg_color="#0a2a4a",
                    text_color="#3498db",
                    text=f"{base_text}\n{hider_label}"
                )
            elif place_num == seeker_pos:
                btn.configure(
                    border_color="#e67e22",
                    fg_color="#3d1a00",
                    text_color="#e67e22",
                    text=f"{base_text}\n{seeker_label}"
                )
            else:
                btn.configure(
                    border_color="#2ecc71",
                    fg_color="#0a0a0a",
                    text_color="#2ecc71",
                    text=base_text
                )

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

        if self.selected_role == "hider":
            hider_pos  = self.selected_place
            seeker_pos = computer_position
        else:
            hider_pos  = computer_position
            seeker_pos = self.selected_place

        self.highlight_round(hider_pos, seeker_pos, self.selected_role)

        if hider_pos == seeker_pos:
            if self.selected_role == "hider":
                messagebox.showinfo(
                    "💀 CAUGHT!",
                    "The computer tracked you down!\nYou've been found , better pick a harder spot next time."
                )
            else:
                messagebox.showinfo(
                    "🎯 GOT THEM!",
                    "You found the hider!\nNice work , your instincts are sharp."
                )

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