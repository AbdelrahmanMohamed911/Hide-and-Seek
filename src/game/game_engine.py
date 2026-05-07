import random
from .models import InputModel, WorldModel, PayoffModel
from .services import computer_move, random_move
from src.solver.computer_solver import solve
import random
import time
class GameEngine:
    def __init__(self, payoff_model, human_role=None, computer_probabilities=None):
        self.payoff_model = payoff_model
        self.human_role = human_role
        self.computer_probabilities = computer_probabilities
        # self.setup_game()

        # scoreboard
        self.human_rounds_won = 0
        self.computer_rounds_won = 0
        self.human_total_score = 0
        self.computer_total_score = 0
        self.round_count = 0

    # def setup_game(self):
    #     self.places = generate_random_places(self.world_size)
    #     self.payoff_matrix = create_Payoff_matrix(self.places)

    def play_round(self, human_position, computer_position):
        # Determine hider and seeker positions based on human role
        if self.human_role == 'hider':
            hider_position = human_position
            seeker_position = computer_position
        else:
            hider_position = computer_position
            seeker_position = human_position

        print(self.human_role)

        # Calculate scores based on the payoff matrix
        hider_payoff = self.payoff_model.matrix[hider_position][seeker_position]
        print(f"Hider payoff: {hider_payoff}")
        if hider_payoff > 0:
            hider_score = hider_payoff
            seeker_score = -1 * hider_payoff
        else:
            hider_score = hider_payoff
            seeker_score = -1 * hider_payoff

        winner = 'hider' if hider_score > seeker_score else 'seeker'

        # Update scoreboard
        self.round_count += 1
        if self.human_role == "hider":
            self.human_total_score += hider_score
            self.computer_total_score += seeker_score
            if winner == 'hider':
                self.human_rounds_won += 1
            else:
                self.computer_rounds_won += 1
        else:
            self.human_total_score += seeker_score
            self.computer_total_score += hider_score
            if winner == 'seeker':
                self.human_rounds_won += 1
            else:
                self.computer_rounds_won += 1

        print(f"Round {self.round_count}: Human ({self.human_role}) score: {hider_score if self.human_role == 'hider' else seeker_score}, Computer score: {seeker_score if self.human_role == 'hider' else hider_score}, Winner: {winner}")

    def play_simulation(self, rounds = 100):
        print(f"Human role: {self.human_role}")
        n = len(self.payoff_model.matrix)

        computer_probabilities_seeker, _ = solve(self.payoff_model, "hider")
        computer_probabilities_hider, _ = solve(self.payoff_model, "seeker")
        
        for _ in range(rounds):
            self.human_role = random.choice(['hider', 'seeker'])
            if self.human_role == "hider":
                self.computer_probabilities = computer_probabilities_seeker
            else:
                self.computer_probabilities = computer_probabilities_hider

            human_position = random_move(n)
            computer_position = computer_move(self.computer_probabilities)
            print(f"Computer chose position: {computer_position}")
            print(f"Human chose position: {human_position}")
            self.play_round(human_position, computer_position)
            delay=0.2
            time.sleep(delay)

    def reset_scoreboard(self):
        self.human_rounds_won = 0
        self.computer_rounds_won = 0
        self.human_total_score = 0
        self.computer_total_score = 0
        self.round_count = 0