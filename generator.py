def parse_expression(expression):
	"""
	Generates a truth table of all possible combination of inputs and outputs 
	for a given boolean expression. Boolean expressions are composed of single-character 
	variables and operations, with no spaces. Does not attempt to clean given expression, 
	and may break if expression is improperly formatted. 

	Operations:
	- AND: .
	- OR: +
	- XOR: #
	- NOT: !

	Arguments:
		expression (str): boolean expression to be parsed

	Usage:
		>>> parse_expression("A.B")
		A B | X
		0 0 | 0
		0 1 | 1
		1 0 | 1
		1 1 | 1
	"""
	operations = {'.':lambda a,b: a&b, '+':lambda a,b: a|b, '#':lambda a,b: a^b}
	non_variables = list(operations.keys()) + ['(', ')', '!']
	variables = [x for x in expression if x in set(expression).difference(non_variables)]

	expression = f"({expression})"

	print(" ".join(variables) + " | X")
	for i in range(0, 2** len(variables)):
		inputs = format(i, f'0{len(variables)}b')
		output = evaluate_expression(expression, variables, inputs, operations)
		print(f"{' '.join(inputs)} | {output}")


def evaluate_expression(expression, variables, inputs, operations):
	"""
	Evaluate given boolean expression for some combination of inputs. 

	Arguments:
		expression (str): boolean expression to be evaluated
		variables (list[str]): list of variables in complete expression
		inputs (str): binary string, with each bit being the input for the variable
		at the same index in 'variables'
		operations (dict[str,lambda]): dictionary of boolean operations 
	
	Returns: (str) Output of expression
	"""
	expression = list(expression)
	
	while len(expression) > 1:
		start = 0
		for i in range(0, len(expression)):
			if expression[i] == "(":
				start = i
			if expression[i] == ")":
				result = compute_output(expression[start:i+1], variables, inputs, operations)
				expression[start:i+1] = result
				break
	return expression[0]

def compute_output(sub, variables, inputs, operations):
	"""
	Compute result of two-variable boolean expression, being a component of some larger
	expression (e.g. C.D in A+(B.(C.D)))

	Arguments:
		sub (list[str]): sub-expression to be evaluated
		variables (list[str]): list of variables in complete expression
		operations (dict[str,lambda]): dictionary of boolean operations

	Returns: (str) Output of sub-expression
	"""
	# Bits to be evaluated
	results = []
	# Operation to be performed
	op = ""
	# Replace variables with appropriate bits
	for i in range(0, len(sub)):
		element = sub[i]
		if element not in (variables + ['0', '1']):
			op = element if element in operations.keys() else op
			continue
		result = -1
		if sub[i-1] == '!':
			result = int(sub[index+1])^1 			
		elif element in variables:
			result = inputs[variables.index(element)]
		else:
			result = element
		results.append(int(result))
	return str(operations[op](results[0], results[1]))
