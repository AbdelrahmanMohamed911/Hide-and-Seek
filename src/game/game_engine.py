from random import random
from .models import InputModel, WorldModel, PayoffModel
from .services import computer_move, random_move

class GameEngine:
    def __init__(self, input_model, world_model, payoff_model, human_role, computer_probabilities):
        self.input_model = input_model
        self.world_model = world_model
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

        # Calculate scores based on the payoff matrix
        hider_payoff = self.payoff_model.matrix[hider_position][seeker_position]
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

    def play_simulation(self, rounds = 100):
        self.human_role = random.choice(['hider', 'seeker'])
        n = len(self.payoff_model.matrix)
        for _ in range(rounds):
            human_position = random_move(n)
            computer_position = computer_move(self.computer_probabilities)
            self.play_round(human_position, computer_position)

    def reset_scoreboard(self):
        self.human_rounds_won = 0
        self.computer_rounds_won = 0
        self.human_total_score = 0
        self.computer_total_score = 0
        self.round_count = 0