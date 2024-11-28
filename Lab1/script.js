class ExpressionParser {
	constructor() {
		this.errors = [];
		this.tokens = [];
	}

	// Lexical token types
	static TOKEN_TYPES = {
		NUMBER: 'number',
		IDENTIFIER: 'identifier',
		OPERATOR: 'operator',
		FUNCTION: 'function',
		PARENTHESIS: 'parenthesis'
	};

	// Supported operators
	static OPERATORS = ['+', '-', '*', '/', '**', '++', '--'];

	// Regex patterns for validation
	static PATTERNS = {
		IDENTIFIER: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
		DECIMAL_NUMBER: /^-?\d+(\.\d+)?$/,
		HEX_NUMBER: /^(0x|0X)[0-9A-Fa-f]+$/,
		BINARY_NUMBER: /^(0b|0B)[01]+$/
	};

	tokenize(expression) {
		this.errors = [];
		this.tokens = [];
		let currentToken = '';
		let position = 0;

		while (position < expression.length) {
			const char = expression[position];

			// Skip whitespaces
			if (/\s/.test(char)) {
				position++;
				continue;
			}

			// Check for multi-character operators
			if (['*', '/', '+', '-'].includes(char)) {
				const nextChar = expression[position + 1];
				if (
					(char === '*' && nextChar === '*') ||
					(char === '+' && nextChar === '+') ||
					(char === '-' && nextChar === '-')
				) {
					this.tokens.push({
						type: ExpressionParser.TOKEN_TYPES.OPERATOR,
						value: char + nextChar,
						position: position
					});
					position += 2;
					continue;
				}
			}

			// Operators
			if (ExpressionParser.OPERATORS.includes(char)) {
				this.tokens.push({
					type: ExpressionParser.TOKEN_TYPES.OPERATOR,
					value: char,
					position: position
				});
				position++;
				continue;
			}

			// Numbers
			if (/\d|\./.test(char)) {
				currentToken = char;
				let dotCount = char === '.' ? 1 : 0;
				let lookahead = position + 1;

				while (lookahead < expression.length) {
					const nextChar = expression[lookahead];
					if (/\d|\./.test(nextChar)) {
						if (nextChar === '.') dotCount++;
						if (dotCount > 1) {
							this.errors.push({
								message: `Зайва десяткова крапка в дробовому числі на позиції ${lookahead}`,
								position: lookahead
							});
						}
						currentToken += nextChar;
						lookahead++;
					} else break;
				}

				if (!ExpressionParser.PATTERNS.DECIMAL_NUMBER.test(currentToken)) {
					this.errors.push({
						message: `Некоректний формат числа на позиції ${position}`,
						position: position
					});
				}

				this.tokens.push({
					type: ExpressionParser.TOKEN_TYPES.NUMBER,
					value: currentToken,
					position: position
				});
				position = lookahead;
				continue;
			}

			// Identifiers and Functions
			if (/[a-zA-Z_]/.test(char)) {
				currentToken = char;
				let lookahead = position + 1;

				while (lookahead < expression.length) {
					const nextChar = expression[lookahead];
					if (/[a-zA-Z0-9_]/.test(nextChar)) {
						currentToken += nextChar;
						lookahead++;
					} else break;
				}

				// Check if it's a function (next character is '(')
				const nextNonWhitespace = expression.slice(lookahead).match(/^\s*\(/);
				if (nextNonWhitespace) {
					this.tokens.push({
						type: ExpressionParser.TOKEN_TYPES.FUNCTION,
						value: currentToken,
						position: position
					});
				} else {
					if (!ExpressionParser.PATTERNS.IDENTIFIER.test(currentToken)) {
						this.errors.push({
							message: `Некоректний ідентифікатор '${currentToken}' на позиції ${position}`,
							position: position
						});
					}
					this.tokens.push({
						type: ExpressionParser.TOKEN_TYPES.IDENTIFIER,
						value: currentToken,
						position: position
					});
				}

				position = lookahead;
				continue;
			}

			// Parentheses
			if (['(', ')'].includes(char)) {
				this.tokens.push({
					type: ExpressionParser.TOKEN_TYPES.PARENTHESIS,
					value: char,
					position: position
				});
				position++;
				continue;
			}

			// Unknown token
			this.errors.push({
				message: `Невідомий токен '${char}' на позиції ${position}`,
				position: position
			});
			position++;
		}

		this.validateSyntax();
		return this.tokens;
	}

	validateSyntax() {
		let parenthesesStack = [];
		let previousToken = null;

		for (let i = 0; i < this.tokens.length; i++) {
			const token = this.tokens[i];

			// Parentheses matching
			if (token.value === '(') {
				parenthesesStack.push(token);
			}
			if (token.value === ')') {
				if (parenthesesStack.length === 0) {
					this.errors.push({
						message: `Зайва закриваюча дужка на позиції ${token.position}`,
						position: token.position
					});
				} else {
					parenthesesStack.pop();
				}
			}

			// Operator sequence validation
			if (token.type === ExpressionParser.TOKEN_TYPES.OPERATOR) {
				if (
					previousToken &&
					previousToken.type === ExpressionParser.TOKEN_TYPES.OPERATOR
				) {
					this.errors.push({
						message: `Неочікуваний оператор '${token.value}' після оператора '${previousToken.value}' на позиції ${token.position}`,
						position: token.position
					});
				}
			}

			previousToken = token;
		}

		// Unclosed parentheses
		if (parenthesesStack.length > 0) {
			const unclosedParenthesis = parenthesesStack[0];
			this.errors.push({
				message: `Відкриваюча дужка не має парної закриваючої на позиції ${unclosedParenthesis.position}`,
				position: unclosedParenthesis.position
			});
		}
	}

	parse(expression) {
		this.tokenize(expression);
		return {
			tokens: this.tokens,
			errors: this.errors
		};
	}
}

// Example usage
const parser = new ExpressionParser();
const testExpression = '-a ++ b - 2v*func((t+2 -, sin(x/*2.01.2), )/8(-)** ';

// -a ++ b - 2v*func((t+2 -, sin(x/*2.01.2), )/8(-)**
const result = parser.parse(testExpression);

console.log('Tokens:', result.tokens);
console.log('Errors:', result.errors);
