import copy
import os
from typing import Callable

import numpy as np
from matplotlib import pyplot as plt

from online_bin_packing.models import Node, Report, Action
from online_bin_packing.system import result_dir


def plot(algorithm_name: str, reports: list[Report]) -> None:
    path_to_file = f'{result_dir}/solver/{algorithm_name}'
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)
    x = [r.time for r in reports]
    plt.plot(x, [len(r.nodes) for r in reports])
    plt.xlabel('time (s)')
    plt.ylabel('vm count')
    plt.title(algorithm_name)
    plt.savefig(f'{path_to_file}/pod_count')
    plt.close()

    plt.plot(x, [r.cpu_utilization for r in reports])
    plt.xlabel('time (s)')
    plt.ylabel('cpu utilization')
    plt.title(algorithm_name)
    plt.savefig(f'{path_to_file}/cpu_utilization')
    plt.close()

    plt.plot(x, [r.memory_utilization for r in reports])
    plt.xlabel('time (s)')
    plt.ylabel('memory utilization')
    plt.title(algorithm_name)
    plt.savefig(f'{path_to_file}/memory_utilization')
    plt.close()

    plt.plot(x, np.cumsum([r.price for r in reports]))
    plt.xlabel('time (s)')
    plt.ylabel('cost ($)')
    plt.title(algorithm_name)
    plt.savefig(f'{path_to_file}/cost')
    plt.close()


def run_solver(
        algorithm_name: str,
        solver: Callable,
        nodes: list[Node],
        activations: list[Action],
        reports: list[Report], **kwargs
) -> list[Node]:
    for node in nodes:
        node.revise_actions()
    nodes: list[Node] = solver(activations=copy.deepcopy(activations), nodes=copy.deepcopy(nodes), **kwargs)
    bin_packing_nodes = list(filter(lambda n: len(n.actions), nodes))
    reports.append(Report(algorithm_name, nodes=bin_packing_nodes))

    plot(algorithm_name, reports)
    return nodes
