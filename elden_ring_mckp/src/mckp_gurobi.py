#! python3

import gurobipy as grb


from armor import ArmorPiece
from data import PIECES, ATTRIBUTES

T = [PIECES.head, PIECES.chest, PIECES.hands, PIECES.legs]


def _value(piece: ArmorPiece, attr_multipliers: dict) -> float:
    """Multiplier sets the priority of each item """
    return sum(getattr(piece, attr) * attr_multipliers.get(piece, 1) 
               for attr in ATTRIBUTES)
    

def solve(budget: float, value: callable):

    # For storing the variables
    armor_ids = {}
    x = {}

    # Initialize the model
    model = grb.Model(f'MCKP with gurobi (B{budget})')
    model.Params.OutputFlag = 0

    # Create and store the variables
    i = 0
    for armor_type in T:
        for piece in armor_type:
            piece.var = model.addVar(vtype=grb.GRB.BINARY)

            armor_ids[i] = piece
            x[i] = piece.var
            i += 1
            
    # Constraints
    # Assignment constraints
    for armor_type in T:
        model.addConstr(grb.quicksum(piece.var for piece in armor_type) == 1)
    
    # Knapsack constraints
    model.addConstr(
        grb.quicksum(piece.var * piece.weight for armor_types in T 
                     for piece in armor_types) <= budget
        )
    
    # Objective
    model.modelSense = grb.GRB.MAXIMIZE
    model.setObjective(grb.quicksum(value(piece) * piece.var 
        for armor_types in T for piece in armor_types)
    )
    
    # Solve    
    model.optimize()

    solution = {piece for t in T for piece in t if piece.var.x > 0}
    return solution, model


if __name__ == "__main__":
    # value function, returns the armor pieces value
    attr_multipliers = {}   # If not given all attributes given equal priority
    value = lambda piece: _value(piece, attr_multipliers)

    x, m = solve(50, value)

    
    for t in T:
        for x in t:
            if x.var.x > 0:
                print(x.name, x.weight)
