import time
from mckp_with_covers_kp import _value, ATTRIBUTES, MCKPWithCovers, T
from mckp_with_covers import MCKPWithCovers as MCKPWithCoversG
from mckp_gurobi import solve

def get_weight_value(x, gurobi=False):
    tw = 0
    tv = 0
    selected_armors = x.values() if not gurobi else x
    for selected_armor in selected_armors:
        print(selected_armor.name, f'(weight={selected_armor.weight})')
        tw += selected_armor.weight
        tv += value(selected_armor)

    return tw, tv

def print_inequalities_latex(ineqs):
    print('\n\n\nAdded Inequalities:')
    for ii, ineq in enumerate(ineqs):
        inq = [f"{ineq_i if ineq_i != 1 else ''}x_{{{i}}}" for i, ineq_i in ineq['alphas'].items()]

        inqq = inq[0]
        for i, iq in enumerate(inq[1:], 1):
            inqq += ' + ' + iq
            if i % 8 == 0:
                inqq += r' \notag \\'
                
        inqq += f' \\leq {len(ineq["cover"]) - 1}'
        print(fr'{inqq} \\')
        

if __name__ == "__main__":
    attr_multipliers = {attr: (len(ATTRIBUTES) - rpriority) for rpriority, attr in enumerate(ATTRIBUTES)}   # If not given all attributes given equal priority
    value = lambda piece: _value(piece, attr_multipliers)

    budget = 30

    # MCKP with covers with cover and lifting with dynamic programming knapsack   
    mckp_instance = MCKPWithCovers(T, value)
    st = time.time()
    x, z, ineqs, fd_ineqs = mckp_instance.solve_MCKP_with_covers(budget, 1, 1000, 10)
    print(f'\n\nMCKP with covers (DP knapsack for cover and lifting) took: {time.time() - st} seconds')
    tw, tv = get_weight_value(x)
    print(f"\nTotal weight = {tw}\nValue = {tv}\nTotal inequalities found = {len(ineqs)}")

    print_inequalities_latex(ineqs)

    # MCKP IP directly by Gurobi
    st = time.time()
    xig, z = solve(budget, value)
    print(f'\n\nMCKP with gurobi IP took: {time.time() - st} seconds')
    tw, tv = get_weight_value(xig, gurobi=True)
    print(f"\nTotal weight = {tw}\nValue = {tv}")


    # MCKP with covers with cover and lifting with Gurobi IP knapsack
    mckp_instance_gurobi = MCKPWithCoversG(T, value)
    st = time.time()
    x, z, ineqsg, fd_ineqsg = mckp_instance_gurobi.solve_MCKP_with_covers(budget, 1, 1000, 10)
    print(f'\n\nMCKP with covers Gurobi took: {time.time() - st} seconds')
    tw, tv = get_weight_value(x)
    print(f"\nTotal weight = {tw}\nValue = {tv}\nTotal inequalities found = {len(ineqsg)}")
    print_inequalities_latex(ineqsg)
