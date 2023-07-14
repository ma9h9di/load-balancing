# Example usage

from online_bin_packing import system
from online_bin_packing.classes import all_action_class
from online_bin_packing.models import Action, Node, Report
from online_bin_packing.solver.bin_packing import bin_packing, BinPackingType
from online_bin_packing.solver.sequential import sequential, shuffle_sequential
from online_bin_packing.system import TIME_SLOT
from online_bin_packing.utils import run_solver


def print_nodes(algorithm: str, nodes: list[Node]):
    all_memory_usage = 0
    all_cpu_usage = 0
    print('------', algorithm, '------')
    for index, node in enumerate(nodes):
        # print(index + 1, node)
        all_memory_usage += node.memory_utilization()
        all_cpu_usage += node.cpu_utilization()
    print()
    if nodes:
        print(f'{len(nodes)}, {round(all_memory_usage / len(nodes), 2)}%, {round(all_cpu_usage / len(nodes), 2)}%')

    print('------', '------', '------', '------')


if __name__ == "__main__":

    actions: dict[int:Action] = {}
    activations = []

    for action_class in all_action_class:
        activations += [action_class.generate_activation() for _ in range(100)]

    # activations += [actions[5]] * 50
    # activations += [actions[2]] * 50

    memory_bin_packing_nodes: list[Node] = []
    memory_bin_packing_reports: list[Report] = []

    cpu_bin_packing_nodes: list[Node] = []
    cpu_bin_packing_reports: list[Report] = []

    both_bin_packing_nodes: list[Node] = []
    both_bin_packing_reports: list[Report] = []

    sequential_nodes: list[Node] = []
    sequential_reports: list[Report] = []

    shuffle_sequential_nodes: list[Node] = []
    shuffle_sequential_reports: list[Report] = []

    for _ in range(int(60 * 2 / TIME_SLOT)):
        memory_bin_packing_nodes = run_solver(
            algorithm_name='memory bin packing',
            solver=bin_packing,
            nodes=memory_bin_packing_nodes,
            activations=activations,
            reports=memory_bin_packing_reports,
            active_nodes=[],
            bin_type=BinPackingType.MEMORY
        )
        cpu_bin_packing_nodes = run_solver(
            algorithm_name='cpu bin packing',
            solver=bin_packing,
            nodes=cpu_bin_packing_nodes,
            activations=activations,
            reports=cpu_bin_packing_reports,
            active_nodes=[],
            bin_type=BinPackingType.CPU
        )
        both_bin_packing_nodes = run_solver(
            algorithm_name='both bin packing',
            solver=bin_packing,
            nodes=both_bin_packing_nodes,
            activations=activations,
            reports=both_bin_packing_reports,
            active_nodes=[],
            bin_type=BinPackingType.BOTH
        )
        sequential_nodes = run_solver(
            algorithm_name='sequential',
            solver=sequential,
            nodes=sequential_nodes,
            activations=activations,
            reports=sequential_reports
        )
        shuffle_sequential_nodes = run_solver(
            algorithm_name='shuffle',
            solver=shuffle_sequential,
            nodes=shuffle_sequential_nodes, activations=activations,
            reports=shuffle_sequential_reports
        )

        system.SYSTEM_TIME += TIME_SLOT
        activations = []
        for action_class in all_action_class:
            activations += [action_class.generate_activation() for _ in range(action_class.get_inter_arrival())]
