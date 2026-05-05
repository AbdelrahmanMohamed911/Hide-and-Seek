import numpy as np
from scipy.optimize import linprog
from src.game.models import PayoffModel

def solve_seeker_minimax(payoff_model: PayoffModel, method='highs'):
    G = payoff_model.matrix
    # n = m always
    n, m = np.shape(G) 
    
    #objective: minimize W
    #  [y1, y2, ..., ym = 0 , W]
    # Minimize W
    c = np.zeros(m + 1)
    c[m] = 1 
    #constraints
    # original constraints: W - a11 y1 - a12y2 - ... - a1m ym >= 0
    # by multiplying by -1 ( to convert to <= for linprog):  a11 y1 + a12y2 + ... + a1m ym -W <= 0
    A_ub = np.append(G, -np.ones((n, 1)), axis=1)
    b_ub = np.zeros(n)
    
    # sum(yj) = 1 (W is not part of the sum)
    A_eq = np.ones((1, m + 1))
    A_eq[0][m] = 0
    b_eq = np.ones(1)

    # Probabilities yj >= 0, W is unrestricted
    bounds = [(0, None)] * m + [(None, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method=method)
    #linprog work with minimization, so the optimal value is in res.fun and not -res.fun as in the hider case
    if res.success:
        return res.x[:-1], res.fun
    return None, None
def main():
    # sheet example
    # expected output: Seeker's Optimal Strategy (Probabilities): [0.5 0.5], Value of the Game (W): 25.0
    payoff_matrix = np.array([[10,40], [30,20]])
    payoff_model = PayoffModel(matrix=payoff_matrix)
    seeker_probs, game_value = solve_seeker_minimax(payoff_model)
    print("Seeker's Optimal Strategy (Probabilities):", seeker_probs)
    print("Value of the Game (W):", game_value)
if __name__ == "__main__":
    main()