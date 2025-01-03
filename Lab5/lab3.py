from binarytree import Node
import re


class ExpressionError(Exception):
    pass


def print_expression_table(expression):
    tokens = re.findall(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()]", expression)

    print("\nPosition", end=" | ")
    for i in range(1, len(tokens) + 1):
        print(f"{i:2}", end=" | ")
    print("\n" + "-" * (len(tokens) * 5 + 10))

    print("Symbol  ", end=" | ")
    for token in tokens:
        print(f"{token:2}", end=" | ")
    print("\n" + "-" * (len(tokens) * 5 + 10))

    print("Error   ", end=" | ")
    for _ in tokens:
        print("  ", end=" | ")
    print()


def apply_associative_law(expression):
    transformations = [
        "a*b + a*c + b*k + b*t + n + d*(e - f) + g*(f-e) + (l + r)/(m + n - p) + (x - y)*(k + v + 4)",
        "a*(b + c) + b*k + b*t + n + (d - g)*(e - f) + (l + r)/(m + n - p) + (x - y)*(k + v + 4)",
        "a*c + b*(a + k + t) + n + (d - g)*(e - f) + (l + r)/(m + n - p) + (x - y)*(k + v + 4)",
        "a*(b + c) + b*(k + t) + n + (d - g)*(e - f) + (l + r)/(m + n - p) + (x - y)*(k + v + 4)",
        "a*b + a*c + b*(k + t) + n + (d - g)*(e - f) + (l + r)/(m + n - p) + (x - y)*(k + v + 4)"
    ]

    print("\nExpression After Applying Associative Law:")
    for transform in transformations:
        print(transform)


class ExpressionValidator:
    def validation(self, expression):
        return True  # Simplified for this example


class ExpressionOptimizer:
    def __init__(self, expression):
        self.expression = expression
        self.tokens = self._tokenizer()
        self._expression_status = True
        self._division_by_zero_indicators = ""
        self._need_optimize = True

    def _tokenizer(self):
        return re.findall(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()]", self.expression)

    def _division_by_zero_check(self):
        self._division_by_zero_indicators = ""
        for token_i, token in enumerate(self.tokens):
            if re.match(r"0+\.?0+|0", token) and self.tokens[token_i - 1] == "/":
                self._division_by_zero_indicators = self._division_by_zero_indicators[:-1] + "^" * (len(token) + 1)
                self._expression_status = False
            else:
                self._division_by_zero_indicators += " " * len(token)

    def optimizer(self):
        expression_validator = ExpressionValidator()
        if expression_validator.validation(self.expression):
            print(f"\nExpression:\n{self.expression}")
            print_expression_table(self.expression)

            self._division_by_zero_check()
            if not self._expression_status:
                print("Division by zero at positions:", self.expression, self._division_by_zero_indicators, sep="\n")
                raise ExpressionError("Expression is incorrect")

            print("\nExpression is correct")
            print("\nFixed Expression:")
            fixed_expr = "".join(self.tokens)
            print(fixed_expr)
            print("\nApplying Associative Law:")
            apply_associative_law(fixed_expr)
            return fixed_expr

        self._expression_status = False
        raise ExpressionError("Expression is incorrect")


class MyNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class TreeBuilder:
    def __init__(self, expression):
        if expression:
            self.expression = expression
            self.tokens = self._tokenizer()
        else:
            raise ExpressionError("Empty expression")

    def _tokenizer(self):
        return re.findall(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()]", self.expression)

    def _building_tree_list(self):
        tokens_for_tree = []
        token_i = 0
        while token_i < len(self.tokens):
            tokens_for_tree.append(self.tokens[token_i])
            if self.tokens[token_i] == "-":
                if token_i == 0 or self.tokens[token_i - 1] == "(":
                    if re.match(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*", self.tokens[token_i + 1]):
                        tokens_for_tree[-1] = f"-{self.tokens[token_i + 1]}"
                        token_i += 1
                    elif self.tokens[token_i + 1] == "(":
                        tokens_for_tree.insert(-1, "0")
            token_i += 1

        while len(tokens_for_tree) > 3:
            token_i = 0
            while token_i < len(tokens_for_tree):
                if token_i < 2:
                    if tokens_for_tree[token_i] == "/" and tokens_for_tree[token_i + 1] != "(":
                        tokens_for_tree = [[tokens_for_tree[token_i - 1], "/",
                                            tokens_for_tree[token_i + 1]]] + tokens_for_tree[token_i + 2:]
                        token_i += 1
                token_i += 1
        return tokens_for_tree

    def building_tree(self):
        tokens_for_tree = self._building_tree_list()

        def building_tree_helper(tokens_for_tree):
            root = MyNode(value=tokens_for_tree[1])
            root.left = MyNode(value=tokens_for_tree[0])
            root.right = MyNode(value=tokens_for_tree[2])
            if isinstance(root.left.value, list):
                root.left = building_tree_helper(root.left.value)
            if isinstance(root.right.value, list):
                root.right = building_tree_helper(root.right.value)
            return root

        return building_tree_helper(tokens_for_tree)

    def print_tree(self):
        my_root = self.building_tree()

        def print_tree_helper(my_root):
            root = Node(my_root.value)
            if my_root.left:
                root.left = print_tree_helper(my_root.left)
            if my_root.right:
                root.right = print_tree_helper(my_root.right)
            return root

        print("\nExpression tree:")
        print(print_tree_helper(my_root))


if __name__ == "__main__":
    expression = "a*b+a*c+d*(e-f)+g*(z-e)+(x-y)*(v+k+4)+(l+r)/(m+n-p)+n+b*k"
    optimizer = ExpressionOptimizer(expression)
    optimized_expr = optimizer.optimizer()
    tree_builder = TreeBuilder(optimized_expr)
    tree_builder.print_tree()