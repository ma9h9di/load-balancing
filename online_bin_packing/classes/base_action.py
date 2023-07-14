import os

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import differential_evolution

from online_bin_packing.models import Action
from online_bin_packing.system import MIN_MEMORY_ACTION, MIN_CPU_ACTION, MAX_CPU_ACTION, \
    MAX_MEMORY_ACTION, PLOT, result_dir


class ActionClass:
    cpu_x = np.linspace(MIN_CPU_ACTION, MAX_CPU_ACTION, 1000).reshape(-1, 1)
    memory_x = np.linspace(MIN_MEMORY_ACTION, MAX_MEMORY_ACTION, 1000).reshape(-1, 1)

    def __init__(
            self, name: str, cpu_pars: list[float],
            memory_pars: list[float], inter_arrival_mean: int
    ):
        self.name: str = name
        self.memory_pars: list[float] = memory_pars
        self.cpu_pars: list[float] = cpu_pars
        self.result_dir = f'{result_dir}/action class/{self.name}'
        self.inter_arrival_mean: int = inter_arrival_mean
        if PLOT and not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        self.__set_best_config()
        self._plot()

    def get_inter_arrival(self) -> int:
        return round(np.random.gamma(shape=self.inter_arrival_mean ** 2, scale=1 / self.inter_arrival_mean))

    def generate_activation(self) -> Action:
        return Action(self)

    def get_lambda_cost_memory(self, memory: int, exec_time: float | None = None):
        exec_time = exec_time if exec_time is not None else self.exec_time(MAX_CPU_ACTION, memory)
        return 0.0000002 + (memory / 1024.0) * exec_time * 0.0001667

    def get_lambda_cost_cpu(self, cpu: float, exec_time: float | None = None):
        exec_time = exec_time if exec_time is not None else self.exec_time(cpu, MAX_MEMORY_ACTION)
        return 0.0000002 + (cpu / 6.0) * exec_time * 0.0867

    def exec_time(self, cpu: float, memory: int):
        return self.exec_time_cpu(cpu) * (
                self.exec_time_memory(memory) / self.exec_time_memory(MAX_MEMORY_ACTION)
        )

    def cost(self, cpu: float, memory: int):
        exec_time = self.exec_time_cpu(cpu) * (
                self.exec_time_memory(memory) / self.exec_time_memory(MAX_MEMORY_ACTION)
        )
        return self.get_lambda_cost_cpu(cpu, exec_time) + self.get_lambda_cost_memory(memory, exec_time)

    def exec_time_memory(self, memory: int):
        pars: list[float] = self.memory_pars
        return pars[0] + pars[1] * (1 - pars[2]) ** (memory - MIN_MEMORY_ACTION)

    def exec_time_cpu(self, cpu: float):
        pars: list[float] = self.cpu_pars
        return pars[0] + pars[1] * (1 - pars[2]) ** (cpu - MIN_CPU_ACTION)

    def __set_best_config(self):
        def objective_function(variables):
            cpu, memory = variables
            return self.get_lambda_cost_cpu(cpu) + self.get_lambda_cost_memory(memory)

        problem = differential_evolution(
            objective_function,
            bounds=[(MIN_CPU_ACTION, MAX_CPU_ACTION), (MIN_MEMORY_ACTION, MAX_MEMORY_ACTION)]
        )

        # Extract the optimal solution
        optimal_solution = problem.x

        self.best_memory = int(optimal_solution[1])
        self.best_cpu = round(optimal_solution[0], 2)

    @property
    def duration_of_best_config(self) -> float:
        return self.exec_time(self.best_cpu, self.best_memory)

    def _plot(self):
        if PLOT:
            self.plot()

    def plot(self):
        self._plot_cost_cpu()
        self._plot_exec_time_cpu()
        self._plot_cost_memory()
        self._plot_exec_time_memory()
        self._plot_exec_time()
        self._plot_cost()
        with open(f'{self.result_dir}/optimal.txt', 'w') as f:
            # Write content to the file
            f.write(f"{self.best_memory}, {self.best_cpu}, {self.duration_of_best_config}\n")
            f.write(f"{self.best_memory / self.best_cpu}\n")
            f.write(f"memory_pars: {self.memory_pars}\n")
            f.write(f"cpu_pars: {self.cpu_pars}\n")
            f.write(f"inter_arrival_mean: {self.inter_arrival_mean}\n")

    def _plot_exec_time_cpu(self):
        cpu_y = self.exec_time_cpu(self.cpu_x)
        plt.plot(self.cpu_x, cpu_y)
        plt.title(f'class {self.name}')
        plt.xlabel('cpu (core)')
        plt.ylabel('duration (s)')
        plt.savefig(f'{self.result_dir}/exec_time_cpu')
        plt.close()

    def _plot_exec_time_memory(self):
        memory_y = self.exec_time_memory(self.memory_x)
        plt.plot(self.memory_x, memory_y)
        plt.title(f'class {self.name}')
        plt.xlabel('memory (mg)')
        plt.ylabel('duration (s)')
        plt.savefig(f'{self.result_dir}/exec_time_memory')
        plt.close()

    def _plot_cost_cpu(self):
        cpu_y = self.get_lambda_cost_cpu(self.cpu_x)
        plt.plot(self.cpu_x, cpu_y)
        plt.title(f'class {self.name}')
        plt.xlabel('cpu (core)')
        plt.ylabel('cost ($)')
        plt.savefig(f'{self.result_dir}/cost_cpu')
        plt.close()

    def _plot_cost_memory(self):
        memory_y = self.get_lambda_cost_memory(self.memory_x)
        plt.plot(self.memory_x, memory_y)
        plt.title(f'class {self.name}')
        plt.xlabel('memory (mg)')
        plt.ylabel('cost ($)')
        plt.savefig(f'{self.result_dir}/cost_memory')
        plt.close()

    def _plot_cost(self):
        X, Y = np.meshgrid(self.cpu_x, self.memory_x)

        # Create the figure and the 3D plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(projection='3d')

        # Plot the surface
        ax.plot_surface(X, Y, self.cost(X, Y))

        # Set labels and title
        ax.set_xlabel('cpu (core)')
        ax.set_ylabel('memory (mg)')
        ax.set_zlabel('cost ($)')
        plt.title(f'class {self.name}')

        plt.savefig(f'{self.result_dir}/3d_cost')
        plt.close()

    def _plot_exec_time(self):
        X, Y = np.meshgrid(self.cpu_x, self.memory_x)

        # Create the figure and the 3D plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(projection='3d')

        # Plot the surface
        ax.plot_surface(X, Y, self.exec_time(X, Y))

        # Set labels and title
        ax.set_xlabel('cpu (core)')
        ax.set_ylabel('memory (mg)')
        ax.set_zlabel('duration')
        plt.title(f'class {self.name}')

        plt.savefig(f'{self.result_dir}/3d_duration')
        plt.close()
