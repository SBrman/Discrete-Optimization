import numpy as np

def knapsack(c, a, b, n, solution=True):
    """Returns the objective value and the solution to the Knapsack instance.
    Args:
    -----
    c = Value of each item
    a = Weight of each item
    b = Maximum weight capacity of the knapsack
    n = Total number of items
    """

    # Create the table
    F = {}

    for h in range(b):
        F.setdefault(0, {}) 
        F[0][h] = 0

    for r in range(1, n):
        F.setdefault(r, {}) 
        F[r][0] = 0

    # Update table
    for r in range(1, n):
        for h in range(1, b):
            if h <= a[r] - 1:
                F[r][h] = F[r-1][h]
            else:
                F[r][h] = max(F[r-1][h], c[r] + F[r-1][h-1])
    
    if solution:
        # Find the knapsack solution
        x = {}
        
        h = b - 1
        for r in range(n-1, 0, -1):
            if F[r][h] == F[r-1][h]:
                x[r] = 0
            else:
                x[r] = 1
                h -= int(np.floor(a[r]))

        return F[n-1][b-1], x
    
    return F[n-1][b-1]
