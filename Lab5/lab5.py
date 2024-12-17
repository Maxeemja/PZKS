from lab2 import ExpressionOptimizer, TreeBuilder
import numpy as np
from typing import List, Optional


class MatrixCell:
    def __init__(self, cell_id, add_duration=1, sub_duration=1, mult_duration=2, div_duration=4):
        self.cell_id = cell_id
        self.memory = []
        self.queue = []
        self.cache = []
        self.operations_duration = {
            "+": add_duration,
            "-": sub_duration,
            "*": mult_duration,
            "/": div_duration
        }
        self.neighbors: List[MatrixCell] = []
        self.local_operations_cache = {}

    def set_neighbors(self, neighbors):
        """Встановлення сусідніх комірок у решітці"""
        self.neighbors = neighbors

    def route_operand(self, operand):
        """Маршрутизація операндів між комірками решітки"""
        # Перевіряємо локальний кеш
        if operand in self.local_operations_cache:
            return self.local_operations_cache[operand]

        # Перевіряємо сусідні комірки
        for neighbor in self.neighbors:
            if operand in neighbor.local_operations_cache:
                return neighbor.local_operations_cache[operand]

        return operand  # Повертаємо оригінальний операнд, якщо не знайдено

    def reading_operands(self, operation, start_calculation_tact):
        def process_operand(operand, operation_type="R"):
            # Маршрутизація операндів
            routed_operand = self.route_operand(operand)

            reading_tact = len(self.memory)

            if reading_tact < len(self.memory):
                self.memory[reading_tact] = (operation_type, routed_operand)
            else:
                self.memory.append((operation_type, routed_operand))

            while reading_tact > len(self.queue):
                self.queue.append(None)
            self.queue.append((operation_type, routed_operand))

        # Логіка читання операндів
        if operation.left.value not in "+-*/" and operation.right.value not in "+-*/":
            process_operand(operand=operation, operation_type="R*")
        elif operation.left.value in "+-*/" or operation.right.value in "+-*/":
            # Обробка субоперацій
            if operation.left.value in "+-*/":
                process_operand(operand=operation.left)
            if operation.right.value in "+-*/":
                process_operand(operand=operation.right)

    def operation_calculation(self, operation):
        start_calculation_tact = len(self.queue)

        self.reading_operands(operation, start_calculation_tact)

        operation_calculation_duration = self.operations_duration[operation.value]
        self.queue.extend([("C", operation)] * operation_calculation_duration)

        writing_tact = len(self.queue)
        self.queue.append(("W", operation))

        # Кешування результату операції
        self.local_operations_cache[operation] = operation

    def print_local_state(self):
        """Виведення локального стану комірки"""
        print(f"Стан комірки {self.cell_id}:")
        print("Черга:", self.queue)
        print("Локальний кеш:", list(self.local_operations_cache.keys()))
        print("---")


class MatrixSystem:
    def __init__(self, rows=2, cols=3,
                 add_duration=1, sub_duration=1,
                 mult_duration=2, div_duration=4):
        self.rows = rows
        self.cols = cols
        self.cells = np.array([
            MatrixCell(f"Cell_{r}_{c}",
                       add_duration, sub_duration,
                       mult_duration, div_duration)
            for r in range(rows)
            for c in range(cols)
        ]).reshape((rows, cols))

        self._configure_topology()
        self.sequential_calculation_time = 0
        self.operations_cache = {}

    def _configure_topology(self):
        """Налаштування зв'язків між комірками у частковій решітці"""
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = []

                # Зв'язки вздовж рядка
                if c > 0:
                    neighbors.append(self.cells[r, c - 1])  # Ліворуч
                if c < self.cols - 1:
                    neighbors.append(self.cells[r, c + 1])  # Праворуч

                # Зв'язки між рядками
                if r > 0:
                    neighbors.append(self.cells[r - 1, c])  # Вгорі
                if r < self.rows - 1:
                    neighbors.append(self.cells[r + 1, c])  # Внизу

                self.cells[r, c].set_neighbors(neighbors)

    def _find_first_available_cell(self, operation):
        """Знаходження першої доступної комірки для обчислення"""
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r, c]
                # Критерії вибору комірки можуть бути складнішими
                if not cell.queue or cell.queue[-1] is None:
                    return cell
        return self.cells[0, 0]  # Повертаємо першу комірку, якщо всі зайняті

    def _calculate_sequential_time(self, operation):
        """Розрахунок часу послідовного виконання операції"""
        time = 0
        if operation.left.value not in "+-*/" and operation.right.value not in "+-*/":
            time += 1
        time += self.cells[0, 0].operations_duration[operation.value] + 1
        return time

    def parallel_calculation(self, expression_root):
        def explore_and_calculate(node):
            if node.value in "+-*/":
                # Рекурсивний обхід лівого та правого операндів
                if node.left.value in "+-*/":
                    explore_and_calculate(node.left)
                if node.right.value in "+-*/":
                    explore_and_calculate(node.right)

                # Вибір комірки та виконання операції
                cell = self._find_first_available_cell(node)
                cell.operation_calculation(node)
                self.sequential_calculation_time += self._calculate_sequential_time(node)

                # Кешування результату
                self.operations_cache[node] = (
                    f"({self.operations_cache.get(node.left, node.left.value)})"
                    f"{node.value}"
                    f"({self.operations_cache.get(node.right, node.right.value)})"
                )

        explore_and_calculate(expression_root)

    def get_system_characteristics(self):
        max_queue_length = max(len(cell.queue) for cell in self.cells.flatten())
        return {
            "sequential_calculation_time": self.sequential_calculation_time,
            "parallel_calculation_time": max_queue_length,
            "acceleration_factor": self.sequential_calculation_time / max_queue_length,
            "system_efficiency": (self.sequential_calculation_time / max_queue_length) / (self.rows * self.cols)
        }

    def print_system_characteristics(self):
        chars = self.get_system_characteristics()
        print("\nХарактеристики системи:")
        for key, value in chars.items():
            print(f"{key.replace('_', ' ')}: {value}")

    def gantt_chart(self):
        print("\nГрафік Ганта для матричної системи:")
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r, c]
                print(f"Комірка {cell.cell_id}:")
                # Виведення черги комірки
                for i, action in enumerate(cell.queue, 1):
                    print(f"Такт {i}: {action}")
                print()


if __name__ == "__main__":
    # Приклад використання
    expression = "a+b+c+d+e+f+g+h"
    print(f"Вираз: {expression}")

    optimized_expression = ExpressionOptimizer(expression).optimizer()
    tree_builder = TreeBuilder(optimized_expression)
    tree_builder.print_tree()
    expression_tree_root = tree_builder.building_tree()

    matrix_system = MatrixSystem(rows=2, cols=3)
    matrix_system.parallel_calculation(expression_tree_root)

    matrix_system.print_system_characteristics()
    matrix_system.gantt_chart()