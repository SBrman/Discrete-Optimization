#! python3

import numpy as np
import gurobipy as grb
from itertools import permutations

from kp import knapsack
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
         
        weights = np.array([self.armor_pieces[i].weight for i in range(self.n)])
        values = np.array([(1 - x_star[i]) for i in range(self.n)])
        budget = self.budget + 1
        
        obj_val, solution = knapsack(a=weights, c=values, b=budget, n=self.n)
        
        solution = {i: sol for i, sol in solution.items() if sol == 1}
        
        return solution, obj_val
    
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
        
        # Case 2: x[t] = 1, 
        # Solve the knapsack problem

        # indeces
        indeces = set(alphas).union(set(cover))
        # To recover the indeces
        indexed_indeces = dict(enumerate(indeces))
        n = len(indexed_indeces)
        
        weights = np.array([self.armor_pieces[indexed_indeces[i]].weight for i in range(n)])
        values = np.array([alphas[indexed_indeces[i]] if indexed_indeces[i] in alphas else 1 for i in range(n)])
        budget = int(np.ceil(self.budget - self.armor_pieces[t].weight))
        
        # Get the alpha for index t
        zeta_t = knapsack(c=values, a=weights, b=budget, n=n, solution=False)
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

            if zeta >= 1:
                if iteration > min_iterations:
                    # Because x* satisfies all cover inequalities at this point.
                    break
                else:
                    # If no cover violation found and min iterations is not exceeded then 
                    # slightly change x^* to get a different cover next iteration
                    x_star[np.random.randint(0, self.n)] = np.random.uniform(0, 1)

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
            
            # Update x_star
            x_star = {i: piece.var.x for i, piece in self.armor_pieces.items()}

            # Increment iteration counter
            iteration += 1

        solution = {i: piece for i, piece in self.armor_pieces.items() if piece.var.x > 0.5}
        
        return solution, model.ObjVal, ineqs, fd_ineqs
