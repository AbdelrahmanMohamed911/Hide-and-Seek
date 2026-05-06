import random
import numpy as np
from src.game.models import InputModel, WorldModel, PayoffModel

PLACE_TYPES = ['neutral', 'easy_for_seeker', 'hard_for_seeker']
PAYOFF_RULES = {
    'neutral': (-1, 1),
    'hard_for_seeker': (-3, 1),
    'easy_for_seeker': (-1, 2)
}

def get_input(n_value , is_1D , proximity) -> InputModel:
    try:
        n = int(n_value)
        if n <= 0:
            raise ValueError("N must be positive")
        return InputModel(n, is_1D, proximity)
    except (ValueError, TypeError) as e:
        print(f"Input Error: {e}")
        return None

def generate_random_places(input_model: InputModel) -> WorldModel:
    if not input_model.is_1D:
        n = input_model.n * input_model.n
    else:
        n = input_model.n
    hardness_list = [random.choice(PLACE_TYPES) for _ in range(n)]
    return WorldModel(input_model, hardness_list)

def create_payoff_matrix(world_model: WorldModel) -> PayoffModel:
    places = world_model.places_hardness
    is_1D = world_model.input_model.is_1D
    proximity = world_model.input_model.proximity
    n = len(places)
    matrix = np.zeros((n, n), dtype=float) #initiate with a matrix full of zeros
    for hiders_position in range(n):
        place_type = places[hiders_position]
        found_payoff,missed_payoff = PAYOFF_RULES[place_type]
        
        for seeker_position in range(n):
            if hiders_position == seeker_position:
                #correct guess for the seekers 
                matrix[hiders_position][seeker_position] = found_payoff
            else:
                if not is_1D:
                    if proximity:
                        hider_row, hider_col = get_coordinates(world_model.input_model, hiders_position)
                        seeker_row, seeker_col = get_coordinates(world_model.input_model, seeker_position)
                        if abs(hider_row - seeker_row) + abs(hider_col - seeker_col) == 1:
                            matrix[hiders_position][seeker_position] = missed_payoff * 0.5 #half the payoff for proximity guess      
                        elif abs(hider_row - seeker_row) + abs(hider_col - seeker_col) == 2:
                            matrix[hiders_position][seeker_position] = missed_payoff * 0.75 #three quarters of the payoff for proximity guess
                        else:
                            matrix[hiders_position][seeker_position] = missed_payoff
                    else:
                        matrix[hiders_position][seeker_position] = missed_payoff
                        
                else:
                    # print(hiders_position, seeker_position , hiders_position - seeker_position)
                    if proximity:
                        if abs(hiders_position - seeker_position) == 1:
                            matrix[hiders_position][seeker_position] = missed_payoff * 0.5 #half the payoff for proximity guess      
                        elif abs(hiders_position - seeker_position) == 2:
                            matrix[hiders_position][seeker_position] = missed_payoff * 0.75 #three quarters of the payoff for proximity guess
                        else:
                            matrix[hiders_position][seeker_position] = missed_payoff
                    else:
                        matrix[hiders_position][seeker_position] = missed_payoff
                    
    return PayoffModel(matrix)
 
def computer_move(probabilities):
    return np.random.choice(len(probabilities), p=probabilities)

def random_move(n):
    return random.randint(0, n-1)

# mapping from 1D index to 2D coordinates
def get_coordinates(input_model, index):
    if input_model.is_1D:
        return index
    else:
        row = index // input_model.n
        col = index % input_model.n
        return (row, col)
# mapping from 2D coordinates to 1D index
def get_1D_index(input_model, row, col):
    if input_model.is_1D:
        return row
    else:
        return row * input_model.n + col