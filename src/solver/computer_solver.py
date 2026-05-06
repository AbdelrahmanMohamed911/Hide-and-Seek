from src.solver.hider_solver import solve_hider_maximin
from src.solver.seeker_solver import solve_seeker_minimax
from src.game.models import PayoffModel

def solve(payoff_model: PayoffModel, human_role: str):
    if human_role == 'hider':
        computer_strategy, game_value = solve_seeker_minimax(payoff_model)
    else:
        computer_strategy, game_value = solve_hider_maximin(payoff_model)
    return computer_strategy, game_value