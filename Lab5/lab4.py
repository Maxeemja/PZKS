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


def apply_distributive_law(tokens):
    def tokenize(expr):
        return re.findall(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()]", expr)

    def find_matching_parenthesis(tokens, start):
        count = 1
        i = start + 1
        while count != 0 and i < len(tokens):
            if tokens[i] == '(':
                count += 1
            elif tokens[i] == ')':
                count -= 1
            i += 1
        return i - 1

    def distribute_terms(a, b):
        result = []
        b_terms = []
        current_term = []

        # Parse b into terms
        i = 0
        while i < len(b):
            if b[i] in ['+', '-'] and not current_term:
                b_terms.extend(current_term)
                current_term = [b[i]]
            else:
                current_term.append(b[i])
            i += 1
        if current_term:
            b_terms.extend(current_term)

        # Distribute a over each term in b
        for term in b_terms:
            if isinstance(term, list):
                result.extend(['*'.join([a] + term)])
            else:
                result.append(f"{a}*{term}")

        return '+'.join(result)

    result = []
    i = 0
    while i < len(tokens):
        if tokens[i] == '*' and i > 0 and i < len(tokens) - 1:
            left = tokens[i - 1]
            right = tokens[i + 1]

            # Handle (a+b)*(c+d) case
            if left == ')' and right == '(':
                left_start = i - 2
                while left_start >= 0 and tokens[left_start] != '(':
                    left_start -= 1
                left_expr = tokens[left_start + 1:i - 1]

                right_end = find_matching_parenthesis(tokens, i + 1)
                right_expr = tokens[i + 2:right_end]

                distributed = distribute_terms(left_expr, right_expr)
                result.extend(tokenize(distributed))
                i = right_end + 1
                continue

        result.append(tokens[i])
        i += 1

    return result


def print_distributive_steps(tokens):
    print("\nExpression After Applying Distributive Law:")
    current = ''.join(tokens)
    print(current)

    distributed = apply_distributive_law(tokens)
    while ''.join(distributed) != current:
        current = ''.join(distributed)
        print(current)
        distributed = apply_distributive_law(distributed)


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
                print("Division by zero at positions:", self.expression,
                      self._division_by_zero_indicators, sep="\n")
                raise ExpressionError("Expression is incorrect")

            print("\nExpression is correct")

            # Apply distributive law transformations
            print("\nExpression After Applying Distributive Law:")
            current_tokens = self.tokens.copy()
            current_expr = "".join(current_tokens)
            print(current_expr)

            while True:
                distributed_tokens = apply_distributive_law(current_tokens)
                new_expr = "".join(distributed_tokens)
                if new_expr == current_expr:
                    break
                print(new_expr)
                current_tokens = distributed_tokens
                current_expr = new_expr

            return current_expr

        self._expression_status = False
        raise ExpressionError("Expression is incorrect")


if __name__ == "__main__":
    expression = "a*b+a*c+d*(e-f)+g*(z-e)+(x-y)*(v+k-7)+(l+r)/(m+n-p)+n+b*k"
    optimizer = ExpressionOptimizer(expression)
    optimized_expr = optimizer.optimizer()
