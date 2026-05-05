import numpy as np

class InputModel:
    def __init__(self, n , is_1D = True , proximity = False):
        self.n = n
        self.is_1D = is_1D
        self.proximity = proximity

class WorldModel:
    def __init__(self, input_model, places_hardness):
        self.input_model = input_model
        self.places_hardness = places_hardness 

class PayoffModel:
    def __init__(self, matrix):
        self.matrix = matrix