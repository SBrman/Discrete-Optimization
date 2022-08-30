Given, a planar graph $G = (V, E)$ and a set of four colors, $C = \left\lbrace 1, 2, 3, 4 \right\rbrace$

Variables:
$$
\begin{align}
    x_{ic} & = \begin{cases}
        1, & \text{if node $i$ is colored with color $c$} \\
        0, & \text{otherwise}
    \end{cases}\\
    z_c & = \begin{cases}
        1, &\text{ if $c$ is assigned to at least one node}\\
        0, &\text{ otherwise}
    \end{cases}
\end{align}
$$

Constraints:
$$
\begin{enumerate}
    \item One color for each node. 
    \begin{align}
        \sum\limits_{j \in C} x_{ij} = 1 && \forall i \in V
    \end{align}
    \item The set of neighbor nodes is denoted by $N(i)$ for node $i$. Nodes $j \in N(i)$ cannot have the same color as $i$
    for all node $i$.
    \begin{align}
        \sum\limits_{k \in N(i)} x_{kc} \leq |N(i)| (1 - x_{ic}) && \forall c \in C
    \end{align}
    \item A color is assigned if at least one node uses that color.
    \begin{align}
        z_c \geq x_{ic} && \forall c \in C ~\forall i \in V
    \end{align}
    \item Binary constraints
    \begin{align}
        x_{ic} \in \left\lbrace 0, 1 \right\rbrace \\
        z_c \in \left\lbrace 0, 1 \right\rbrace 
    \end{align}
\end{enumerate}
$$

Objective:
$$
\begin{align}
    \min\limits_{c \in C} z_c
\end{align}
$$
