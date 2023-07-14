import copy

from online_bin_packing import system
from online_bin_packing.system import NODE_PRICE_TIME_SLOT


class Action:
    def __init__(self, action_class: 'ActionClass'):
        self.action_class: 'ActionClass' = action_class
        self.memory: int = self.action_class.best_memory
        self.cpu: float = self.action_class.best_cpu
        self.start_time: int | None = None
        self.node: Node | None = None

    def add_to_node(self, node: 'Node'):
        self.node = node
        self.start_time = system.SYSTEM_TIME

        self.node.start_action(action=self)

    def __str__(self):
        return f'[{self.action_class.name}], ({self.cpu}, {self.memory}), {self.duration}'

    @property
    def stop(self) -> bool:
        return self.time_to_end <= 0

    @property
    def time_to_end(self) -> float:
        return self.start_time + self.duration - system.SYSTEM_TIME

    @property
    def duration(self) -> float:
        return self.action_class.exec_time(self.cpu, self.memory)

    def revise(self, wight: float, config_type: str):
        if config_type == 'cpu':
            self.cpu *= wight
        elif config_type == 'memory':
            self.memory *= wight


class Node:
    def __init__(self, memory: int, cpu: float):
        self.memory: int = memory
        self.cpu: float = cpu
        self.actions = []

    def cpu_utilization(self) -> float:
        return round(self.usage_cpu / (self.usage_cpu + self.free_cpu), 2)

    def memory_utilization(self) -> float:
        return round(self.usage_memory / (self.usage_memory + self.free_memory), 2)

    def start_action(self, action: Action):
        self.actions.append(action)

    def stop_action(self, action: Action):
        self.actions.remove(action)

    def __str__(self):
        return f'{self.memory_utilization()}, {self.cpu_utilization()}'

    def can_run_action(self, activation: 'Action'):
        return self.free_cpu >= activation.cpu and self.free_memory >= activation.memory

    def revise_actions(self):
        for action in self.actions:
            if action.stop:
                self.stop_action(action)

    @property
    def usage_cpu(self) -> float:
        return sum([a.cpu for a in self.actions])

    @property
    def usage_memory(self) -> float:
        return sum([a.memory for a in self.actions])

    @property
    def free_cpu(self) -> float:
        return self.cpu - self.usage_cpu

    @property
    def free_memory(self) -> float:
        return self.memory - self.usage_memory

    @property
    def time_to_end(self) -> float:
        return max([a.time_to_end for a in self.actions])

    def re_config_cpu(self):
        w_cpu = self.cpu / self.usage_cpu
        for a in self.actions:
            a.revise(w_cpu, 'cpu')

    def re_config_memory(self):
        w_memory = self.memory / self.usage_memory
        for a in self.actions:
            a.revise(w_memory, 'memory')


class Report:

    def __init__(self, algorithm: str, nodes: list[Node]):
        self.time = system.SYSTEM_TIME
        self.nodes = copy.deepcopy(nodes)
        self.algorithm = algorithm

        all_memory_usage = 0
        all_cpu_usage = 0
        for index, node in enumerate(nodes):
            # print(index + 1, node)
            all_memory_usage += node.memory_utilization()
            all_cpu_usage += node.cpu_utilization()
        self.cpu_utilization = all_cpu_usage / len(nodes)
        self.memory_utilization = all_memory_usage / len(nodes)

        self.price = NODE_PRICE_TIME_SLOT * len(nodes)
        self.cpu_waste_price = (1 - self.cpu_utilization) * self.price
        self.memory_waste_price = (1 - self.memory_utilization) * self.price
