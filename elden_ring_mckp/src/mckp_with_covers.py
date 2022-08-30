#! python3

import gurobipy as grb
from itertools import permutations

from armor import ArmorPiece
from data import PIECES, ATTRIBUTES
from mckp_gurobi import solve

T = [PIECES.head, PIECES.chest, PIECES.hands, PIECES.legs]


def _value(piece: ArmorPiece, attr_multipliers: dict) -> float:
    """Multiplier sets the priority of each item """
    return sum(getattr(piece, attr) * attr_multipliers.get(piece, 1) 
               for attr in ATTRIBUTES)

   
class HashableDict(dict):
    """To store inequalities as dictionaries in a set."""
    def __hash__(self):
        return hash(frozenset(self))

   
class MCKPWithCovers:
    def __init__(self, T: list[set], value: callable):

        self.value = value
        self.T = T
        self.budget = None
        
        self.armor_pieces = {}
        i = 0
        for armor_type in self.T:
            for piece in armor_type:
                self.armor_pieces[i] = piece
                i += 1
                
        self.n = len(self.armor_pieces)
        
    def lp_MCKP(self, verbose=0):
        """
        Returns the LP MCKP model.
        """
        # Initialize the model
        model = grb.Model(f'MCKP with covers (B={self.budget})')
        model.Params.OutputFlag = verbose

        # Create and store the variables
        for piece in self.armor_pieces.values():
            # Continuous variables
            piece.var = model.addVar(lb=0, ub=1, vtype=grb.GRB.CONTINUOUS, name=piece.name)
                
        # Constraints
        # Assignment constraints
        for armor_type in T:
            model.addConstr(grb.quicksum(piece.var for piece in armor_type) == 1)
        
        # Knapsack constraints
        model.addConstr(
            grb.quicksum(piece.var * piece.weight for armor_types in T 
                        for piece in armor_types) <= self.budget
            )
        
        # Objective
        model.modelSense = grb.GRB.MAXIMIZE
        model.setObjective(
            grb.quicksum(self.value(piece) * piece.var for armor_types in T 
                        for piece in armor_types)
        )
        
        # Solve
        model.optimize()

        return model
    
    def get_cover(self, x_star: dict, verbose=0) -> tuple[dict, float]:
        """Returns the cover and the objective value"""
        
        model = grb.Model("Cover")
        model.Params.OutputFlag = verbose

        # Variables
        z = model.addVars(self.n, vtype=grb.GRB.BINARY)

        # Constraints
        model.addConstr(
            grb.quicksum(self.armor_pieces[i].weight * z[i] for i in range(self.n)) >= self.budget + 1
        )
        
        # Objective
        model.setObjective(grb.quicksum((1 - x_star[i]) * z[i] for i in range(self.n)))
        
        # Solve
        model.optimize()
        
        solution = {i for i in range(self.n) if z[i].x > 0}
        return solution, model.ObjVal
    
    def lift(self, cover: dict, alphas: dict, t: int, verbose=0) -> int:
        """
        Returns alpha for the variable for the given t 
        after lifting the variable for the given t, cover and the KP instance.
        """

        if t in cover:
            return 1
        elif t in alphas:    # If already lifted
            return alphas[t]
        
        # Case 1: x[t] = 0, inequality created by the input cover and alphas is valid
        # Nothing to do
        
        # Case 2: x[t] = 1
        model = grb.Model("Lifting")
        if not verbose: model.Params.OutputFlag = 0
        
        # Variables with x[t] set to 1, for other indeces binary variables are created.
        x = {i: model.addVar(vtype=grb.GRB.BINARY, name=f'x_{i}') 
             for i in range(self.n) if i != t}
        
        # Constraints
        indeces = set(alphas).union(set(cover))
        model.addConstr(
            grb.quicksum(self.armor_pieces[i].weight * x[i] for i in indeces)
            <= self.budget - self.armor_pieces[t].weight
        )

        if verbose:
            print('Constraints: ' + ' + '.join(f'{self.armor_pieces[i].weight} * x_{i}' for i in alphas) 
                + ' + ' + ' + '.join(f'{self.armor_pieces[i].weight} * x_{i}' for i in cover) 
                + f' <= {self.budget} - {self.armor_pieces[t].weight}')
        
        # Objective
        model.setObjective(
            grb.quicksum(alpha_i * x[i] for i, alpha_i in alphas.items())
            + grb.quicksum(x[i] for i in cover)
        )
        
        model.ModelSense = grb.GRB.MAXIMIZE
        
        # Solve
        model.optimize()
        
        # Get the alpha for index t
        zeta_t = model.ObjVal
        alpha = len(cover) - 1 - zeta_t
        
        return alpha if alpha > 0 else 0
    
    def solve_MCKP_with_covers(self, budget: float, max_permutations=5, max_iterations=1000, min_iterations=1) -> tuple[dict, float]:
        """
        Returns the solution in a dictionary and the objective value of the problem.
        MCKP solver with covers.
        """
        self.budget = budget
        
        ineqs = set()
        fd_ineqs = set()
        n = len(self.armor_pieces)
        
        model = self.lp_MCKP()
        
        x_star = {i: piece.var.x for i, piece in self.armor_pieces.items()}
        alphas = {}

        iteration = 0
        while iteration < max_iterations:
            
            # Find cover for that x*
            cover, zeta = self.get_cover(x_star)

            if zeta >= 1 and iteration > min_iterations:
                # Because x* satisfies all cover inequalities at this point.
                break

            # Sequential Lifting:
            # Get ordering
            ordering = list(set(range(n)) - set(alphas.keys()))

            # Permute the ordering and lift to get more inequalities
            permuted_orderings = permutations(ordering, len(ordering))
            
            for ii, permuted_ordering in enumerate(permuted_orderings):
                
                # Maximum allowed permutations of the orderings
                if ii > max_permutations:
                    break
                
                # Turn the tuple of permuted ordering into indexable list
                permuted_ordering = list(permuted_ordering)

                # Reset alphas to try a different ordering
                new_alphas = alphas
                
                while len(permuted_ordering) != 0:
                    # Stop if t == r meaning alpha for the last index of the ordering is done.
                    
                    # Choose an index, t
                    t = permuted_ordering.pop()

                    # Perform Lifting
                    alpha_t = self.lift(cover, new_alphas, t)

                    # Add alpha_t to the alphas if greater than 0
                    if alpha_t:
                        new_alphas[t] = alpha_t
                        
                    # Put the new inequality in a set
                    if len(new_alphas) > 0:
                        na = {'alphas': new_alphas.copy(), 'cover': cover}
                        ineqs.add(HashableDict(na))
                    
                fd_ineqs.add(HashableDict(na))

            # Add the new inequalities to the master problem and solve it.
            for ineq in ineqs:
                model.addConstr(
                    grb.quicksum(ineq_i * self.armor_pieces[i].var
                                 for i, ineq_i in ineq['alphas'].items()) <= len(ineq['cover']) - 1
                )
            model.update()
            model.optimize()
            
            # Update x*
            x_star = {i: piece.var.x for i, piece in self.armor_pieces.items()}

            # Increment iteration counter
            iteration += 1

        solution = {i: piece for i, piece in self.armor_pieces.items() if piece.var.x > 0.5}
        
        return solution, model.ObjVal, ineqs, fd_ineqs
