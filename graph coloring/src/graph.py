#! python3 

__author__ = "Simanta Barman"
__email__ = "barma017@umn.edu"

# %%
from typing import Union

Node = Union[str, int]
Edge = tuple[Node, Node]


class Graph:

    def __init__(self, V: set[Node], E: set[Edge]):
        
        self.vertices = V
        self._graph: dict[Node, set[Node]] = {} 
        self.update_graph(E)
        
    def update_graph(self, E: set[Edge]):
        for e in E:
            for i, j in [e, e[::-1]]:
                self._graph.setdefault(i, set())
                self._graph[i].add(j)
    
    @property
    def edges(self):
        for i, nodes in self._graph.items():
            for j in nodes:
                yield (i, j)

    def neighbours(self, node):
        for j in self._graph[node]:
            yield j
        

def problem5_graph() -> Graph:
                
    E = {(1, 2), (1, 5), 
        (2, 3), (2, 5), 
        (3, 4), (3, 6), 
        (4, 6), (4, 7), 
        (5, 6), (5, 7), 
        (6, 7)}

    V = set(v for e in E for v in e)

    return Graph(V, E)

# %% 
if __name__ == "__main__":

    G = problem5_graph()
    
    for v in G.vertices:
        print(f"Neighbours of {v=}: ", end='')
        for nv in G.neighbours(v):
            print(nv, end=', ')
        print('\b\b')


# %%
