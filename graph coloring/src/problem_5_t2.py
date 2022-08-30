#! python3 

__author__ = "Simanta Barman"
__email__ = "barma017@umn.edu"

# %%
from graph import *
from gurobipy import GRB, Model, quicksum
EPSILON = 1e-3

# %%
if __name__ == "__main__":

    # G = problem5_graph()
    
    E = {(1, 2), (2, 3), (3, 1)}
    V = {1, 2, 3}
    G = Graph(V, E) 

    model = Model('HW1_Problem5')

    # Variables
    # Color of each node in {1, 2, 3, 4}
    x = model.addVars(G.vertices, vtype=GRB.INTEGER, lb=1, ub=4)

    # a_ij = 1 if x_i != x_j else 0
    vv = [(i, j) for i in G.vertices for j in G.vertices if i != j]
    a = model.addVars(vv, vtype=GRB.BINARY)
    z1 = model.addVars(vv, vtype=GRB.BINARY)
    z2 = model.addVars(vv, vtype=GRB.BINARY)

    # %%
    # Constraints
    # Neighbors can not have the same color
    model.addConstrs(quicksum(a[i, j] for j in G.neighbours(i)) <= 0 for i in G.vertices)
    # model.addConstrs(quicksum(a[i, j] for j in G.neighbours(i)) >= 0 for i in G.vertices)

    model.addConstrs(3 * (1 - z1[i, j]) >= (x[i] - x[j]) for i, j in vv)
    model.addConstrs(3 * (1 - z2[i, j]) >= (x[j] - x[i]) for i, j in vv)
    model.addConstrs(a[i, j] >= z1[i, j] for i, j in vv) 
    model.addConstrs(a[i, j] >= z2[i, j] for i, j in vv) 

    # %%
    model.modelSense = GRB.MAXIMIZE
    model.setObjective(quicksum(a))
    
    model.optimize()
# %%
    
# %%
