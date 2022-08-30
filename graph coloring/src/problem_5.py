#! python3 

__author__ = "Simanta Barman"
__email__ = "barma017@umn.edu"

# %%
from graph import *
from gurobipy import GRB, Model, quicksum

# %%
if __name__ == "__main__":

    G = problem5_graph()
    
    # Color of each node in {1, 2, 3, 4}
    # C = {1, 2, 3, 4, 5}   # got 4 colors solution
    C = {"Red", "Green", "Blue", "Yellow"}

    model = Model('HW1_Problem5')

    # Variables
    # x_ic = 1 if node i is colored c, else 0
    x = model.addVars(((i, c) for i in G.vertices for c in C), vtype=GRB.BINARY)

    # z_c = 1 if c is assigned to at least one node, else 0
    z = model.addVars(C, vtype=GRB.BINARY)
    
    # Constraints
    model.addConstrs(quicksum(x[i, c] for c in C) == 1 for i in G.vertices)
    for i in G.vertices:
        M = len(list(G.neighbours(i)))
        for c in C:
            model.addConstr(z[c] >= x[i, c])
            model.addConstr(quicksum(x[k, c] for k in G.neighbours(i)) <= M * (1 - x[i, c]))
    
    model.modelSense = GRB.MINIMIZE
    model.setObjective(quicksum(z))
    
    model.optimize()
    
    # Solution in Node-Color pair
    solution = {k[0]: k[1] for k, v in x.items() if v.x > 0}

# %%
