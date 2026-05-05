import customtkinter as ctk
from tkinter import messagebox
from src.game.services import get_input, generate_random_places, create_payoff_matrix

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

class PayoffGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HIDE & SEEK: STRATEGY ENGINE")
        self.geometry("600x650")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.header_label = ctk.CTkLabel(
            self, 
            text="MISSION PARAMETERS", 
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
            text_color="#2ecc71"  
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.input_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=2, border_color="#2ecc71")
        self.input_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")

        self.label_n = ctk.CTkLabel(self.input_frame, text="WORLD SIZE (N):", font=("Courier", 14))
        self.label_n.pack(pady=(10, 0))
        
        self.entry_n = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Enter N...", 
            width=200, 
            fg_color="#000000", 
            border_color="#3498db"
        )
        self.entry_n.pack(pady=10)
        self.entry_n.insert(0, "4")

        self.check_1d = ctk.CTkCheckBox(self.input_frame, text="1D DIMENSION(2D NOT IMPLEMENTED YET)", text_color="#3498db", font=("Courier", 12))
        self.check_1d.select()
        self.check_1d.pack(side="left", padx=30, pady=15)

        self.check_proximity = ctk.CTkCheckBox(self.input_frame, text="PROXIMITY RADAR", text_color="#3498db", font=("Courier", 12))
        self.check_proximity.pack(side="right", padx=30, pady=15)

        self.btn_generate = ctk.CTkButton(
            self, 
            text="INITIALIZE PAYOFF MATRIX", 
            command=self.run_logic,
            font=("Courier", 16, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45
        )
        self.btn_generate.grid(row=3, column=0, padx=30, pady=20, sticky="ew")

        self.console_label = ctk.CTkLabel(self, text="SYSTEM DATA OUTPUT:", font=("Courier", 12), text_color="#95a5a6")
        self.console_label.grid(row=4, column=0, padx=30, sticky="w")
        
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

            world_m = generate_random_places(input_m)
            payoff_m = create_payoff_matrix(world_m)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", f"> WORLD GENERATED: {world_m.places_hardness}\n")
            self.output_text.insert("end", "> CALIBRATING PAYOFFS...\n")
            self.output_text.insert("end", "> MATRIX READY:\n\n")
            self.output_text.insert("end", str(payoff_m.matrix))

        except Exception as e:
            messagebox.showerror("SYSTEM CRITICAL", f"Error: {str(e)}")