import numpy as np
from scipy.optimize import linprog
from src.game.models import PayoffModel

def solve_hider_maximin(payoff_model: PayoffModel, method='highs'):
    G = payoff_model.matrix
    # n = m always
    n, m = np.shape(G)
    
    #objective: maximize z 
    #  [x1, x2, ..., xn, z]
    # linprog minimizes, so minimize -z to maximize z
    c = np.zeros(n + 1)
    c[n] = -1 
    # Constraints:
    # z - sum(xi * G_i,j) <= 0  => Ax <= b
    A_ub = np.transpose(-G)
    A_ub = np.append(A_ub, np.ones((m, 1)), axis=1)
    b_ub = np.zeros(m)

    # sum(xi) = 1 (z is not part of the sum)
    A_eq = np.ones((1, n + 1))
    A_eq[0][n] = 0
    b_eq = np.ones(1)

    # Probabilities xi >= 0, z is unrestricted
    bounds = [(0, None)] * n + [(None, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method=method)
    #linprog work with minimization, so the optimal value is -res.fun for the hider's maximin problem cuz we minimized -z instead of maximizing z
    if res.success:
        return res.x[:-1], -res.fun 
    return None, None
# def main():
#     # sheet example
#     # expected output: Hider's Optimal Strategy (Probabilities): [0.25 0.75], Value of the Game (z): 25.0
#     payoff_matrix = np.array([[10,40], [30,20]])
#     payoff_model = PayoffModel(matrix=payoff_matrix)
#     hider_probs, game_value = solve_hider_maximin(payoff_model)
#     print("Hider's Optimal Strategy (Probabilities):", hider_probs)
#     print("Value of the Game (z):", game_value)
# if __name__ == "__main__":
#     main()