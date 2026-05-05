import customtkinter as ctk
from tkinter import messagebox
from src.game.services import get_input, generate_random_places, create_payoff_matrix

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PayoffGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Game Theory: Payoff Matrix Generator")
        self.geometry("500x550")

        self.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self, text="Hider-Seeker Payoff Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        self.entry_n = ctk.CTkEntry(self, placeholder_text="Enter World Size (N)")
        self.entry_n.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry_n.insert(0, "3")

        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.check_1d = ctk.CTkCheckBox(self.config_frame, text="1D World(2D Not implemented yet)")
        self.check_1d.select() 
        self.check_1d.pack(side="left", padx=20, pady=10)

        self.check_proximity = ctk.CTkCheckBox(self.config_frame, text="Proximity Payoffs")
        self.check_proximity.pack(side="left", padx=20, pady=10)

        self.btn_generate = ctk.CTkButton(self, text="Generate Matrix", command=self.run_logic, fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_generate.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.output_text = ctk.CTkTextbox(self, height=200)
        self.output_text.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

    def run_logic(self):
        try:
            n_val = self.entry_n.get()
            is_1d = self.check_1d.get()
            prox = self.check_proximity.get()
            
            input_m = get_input(n_val, is_1d, prox)
            
            if not input_m:
                messagebox.showerror("Input Error", "Please enter a valid positive integer for N.")
                return

            world_m = generate_random_places(input_m)
            payoff_m = create_payoff_matrix(world_m)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", f"Layout: {world_m.places_hardness}\n\n")
            self.output_text.insert("end", "Payoff Matrix:\n")
            self.output_text.insert("end", str(payoff_m.matrix))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate: {str(e)}")

