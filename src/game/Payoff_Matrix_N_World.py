import numpy as np
import random

#defining the types of places we have 
PLACE_Types = ['neutral','easy_for_seeker','hard_for_seeker']

#defining the payoffs 
Pay_off = {
    'neutral':(-1,1),
    'hard_for_seeker':(-3,1),
    'easy_for_seeker':(-1,2)
}

#generating the random array of size n to tell the places
def generate_random_places(n):
    return [random.choice(PLACE_Types) for _ in range(n)]

def create_Payoff_matrix(places):
    n = len(places)
    matrix = np.zeros((n,n) , dtype= int) #initiate with a matrix full of zeros
    
    for hiders_position in range(n):
        place_type = places[hiders_position]
        found_payoff,missed_payoff = Pay_off[place_type]
        
        for seeker_position in range(n):
            if hiders_position == seeker_position:
                #correct guess for the seekers 
                matrix[hiders_position][seeker_position] = found_payoff
            else:
                #wrong guess not a diagonal element
                matrix[hiders_position][seeker_position] = missed_payoff
    return matrix

# if __name__ == "__main__":
#     try:
#         # 1. Ask the user for the size of the world (n)
#         user_input = input("Enter the size of the world (N): ")
#         n = int(user_input)
        
#         if n <= 0:
#             print("Please enter a positive integer greater than 0.")
#         else:
#             # 2. Generate a fully random world of size N
#             random_world = generate_random_places(n)
            
#             print(f"\n--- Random World Layout (Size {n}) ---")
#             for i, place in enumerate(random_world):
#                 # Using i+1 just to make the display 1-indexed for readability
#                 print(f"Location {i+1}: {place}")
            
#             # 3. Create and print the payoff matrix
#             payoff_matrix = create_Payoff_matrix(random_world)
            
#             print("\n--- Hider's Payoff Matrix ---")
#             print(payoff_matrix)
            
#     except ValueError:
#         print("Invalid input. Please enter a valid number.")