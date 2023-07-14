import random

from online_bin_packing.models import Action, Node
from online_bin_packing.system import NODE_CPU, NODE_MEMORY


def sequential(activations: list[Action], nodes: list[Node]) -> list[Node]:
    random.shuffle(nodes)
    node_count = 0
    action_count = 0
    while True:
        if action_count == len(activations):
            return nodes
        if node_count == len(nodes):
            nodes.append(Node(NODE_MEMORY, NODE_CPU))
            continue
        node = nodes[node_count]
        activation = activations[action_count]
        if not node.can_run_action(activation):
            node_count += 1
            continue
        activation.add_to_node(node)
        action_count += 1


def shuffle_sequential(activations: list[Action], nodes: list[Node]) -> list[Node]:
    w_activations = activations.copy()
    random.shuffle(w_activations)
    return sequential(w_activations, nodes)
