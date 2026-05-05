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
                    #To do
                    pass
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