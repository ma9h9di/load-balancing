import random
from enum import Enum

from pulp import *

from online_bin_packing.models import Action, Node
from online_bin_packing.system import NODE_CPU, NODE_MEMORY


class BinPackingType(Enum):
    CPU = 'cpu'
    MEMORY = 'memory'
    BOTH = 'both'


def bin_packing(
        activations: list[Action],
        nodes: list[Node],
        active_nodes: list[Node],
        bin_type: BinPackingType = BinPackingType.BOTH
) -> list[Node]:
    w_activations = activations.copy()
    random.shuffle(w_activations)
    num_items = len(w_activations)
    num_bins = len(active_nodes)
    # Create a new problem instance
    problem = LpProblem("2D_Bin_Packing", LpMinimize)

    # Create binary variables for item placement
    var_names = [f"x{i}_{j}" for i in range(num_items) for j in range(num_bins)]
    variables = LpVariable.dicts("Variables", var_names, 0, 1, LpBinary)

    # Set objective function
    objective_cuffs = [1] * (num_items * num_bins)
    problem += lpSum(
        [variables[var_name] * objective_coeff for var_name, objective_coeff in zip(var_names, objective_cuffs)])

    # Add constraints to ensure each item is placed in exactly one bin
    for i in range(num_items):
        constraint = LpAffineExpression(
            [(variables[var_name], 1) for var_name in var_names[i * num_bins: (i + 1) * num_bins]])
        problem += constraint == 1

    # Add constraints to ensure bin capacity is not exceeded
    for j in range(num_bins):
        if bin_type != BinPackingType.CPU:
            constraint_memory = LpAffineExpression(
                [(variables[var_names[i * num_bins + j]], w_activations[i].memory) for i in range(num_items)])
            problem += constraint_memory <= active_nodes[j].free_memory

        if bin_type != BinPackingType.MEMORY:
            constraint_cpu = LpAffineExpression(
                [(variables[var_names[i * num_bins + j]], w_activations[i].cpu) for i in range(num_items)])
            problem += constraint_cpu <= active_nodes[j].free_cpu

    # Create the solver with a timeout of 60 seconds
    solver = getSolver('PULP_CBC_CMD', timeLimit=60, msg=False)

    # Solve the problem
    problem.solve(solver)

    # Check the solution status
    if LpStatus[problem.status] != 'Optimal':
        if nodes:
            nodes = sorted(nodes, key=lambda n: n.time_to_end, reverse=True)
            active_nodes.append(nodes.pop(0))
        else:
            active_nodes.append(Node(NODE_MEMORY, NODE_CPU))
        return bin_packing(activations=activations, nodes=nodes, active_nodes=active_nodes, bin_type=bin_type)

    # Get the solution
    result_nodes: dict[int:Node] = {}
    for j in range(num_bins):
        node: Node = active_nodes[j]
        sum_usage = {
            BinPackingType.CPU: 0,
            BinPackingType.MEMORY: 0,
        }
        for i in range(num_items):
            if variables[var_names[i * num_bins + j]].value() > 0.5:
                w_activations[i].add_to_node(node)
                sum_usage[BinPackingType.CPU] += w_activations[i].cpu
                sum_usage[BinPackingType.MEMORY] += w_activations[i].memory
                result_nodes[j] = node
        while node.free_memory < 0:
            node.re_config_memory()
        while node.free_cpu < 0:
            node.re_config_cpu()
    return active_nodes + nodes
