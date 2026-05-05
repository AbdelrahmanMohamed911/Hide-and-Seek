import numpy as np
import random
import sys

from services import create_payoff_matrix, get_input , generate_random_places
from models import InputModel, WorldModel, PayoffModel


if __name__ == "__main__":
    try:
        user_input = input("Enter the size of the world (N): ")
        n = int(user_input)
        input_is1D = input("Is the world 1D? (yes/no): ").strip().lower() == 'yes'
        input_proximity = input("Enable proximity payoffs? (yes/no): ").strip().lower() == 'yes'
        
        input_m = get_input(n,input_is1D , input_proximity)
        
        if not input_m:
            sys.exit()
        
        world_m = generate_random_places(input_m )
        payoff_m = create_payoff_matrix(world_m)
    
        print(f"World Size: {payoff_m.matrix.shape[0]}")
        print(f"Hardness List: {world_m.places_hardness}")
        print("Matrix Result:")
        print(payoff_m.matrix)
    #     if n <= 0:
    #         print("Please enter a positive integer greater than 0.")
    #     else:
    #         # 2. Generate a fully random world of size N
    #         random_world = generate_random_places(n)
            
    #         print(f"\n--- Random World Layout (Size {n}) ---")
    #         for i, place in enumerate(random_world):
    #             # Using i+1 just to make the display 1-indexed for readability
    #             print(f"Location {i+1}: {place}")
            
    #         # 3. Create and print the payoff matrix
    #         payoff_matrix = create_Payoff_matrix(random_world )
            
    #         print("\n--- Hider's Payoff Matrix ---")
    #         print(payoff_matrix)
            
    except ValueError:
        print("Invalid input. Please enter a valid number.")

#defining the types of places we have 
# PLACE_Types = ['neutral','easy_for_seeker','hard_for_seeker']

# #defining the payoffs 
# Pay_off = {
#     'neutral':(-1,1),
#     'hard_for_seeker':(-3,1),
#     'easy_for_seeker':(-1,2)
# }

#generating the random array of size n to tell the places
# def generate_random_places(n):
#     return [random.choice(PLACE_Types) for _ in range(n)]

# def create_Payoff_matrix(places, is_1D = True , proximity = False):
#     n = len(places)
#     matrix = np.zeros((n,n) , dtype= float) #initiate with a matrix full of zeros
    
#     for hiders_position in range(n):
#         place_type = places[hiders_position]
#         found_payoff,missed_payoff = Pay_off[place_type]
        
#         for seeker_position in range(n):
#             if hiders_position == seeker_position:
#                 #correct guess for the seekers 
#                 matrix[hiders_position][seeker_position] = found_payoff
#             else:
#                 if not is_1D:
#                     #To do
#                     pass
#                 else:
#                     print(hiders_position, seeker_position , hiders_position - seeker_position)
#                     if proximity:
#                         if abs(hiders_position - seeker_position) == 1:
#                             matrix[hiders_position][seeker_position] = missed_payoff * 0.5 #half the payoff for proximity guess      
#                         elif abs(hiders_position - seeker_position) == 2:
#                             matrix[hiders_position][seeker_position] = missed_payoff * 0.75 #three quarters of the payoff for proximity guess
#                         else:
#                             matrix[hiders_position][seeker_position] = missed_payoff
#                     else:
#                         matrix[hiders_position][seeker_position] = missed_payoff
                
#     return matrix