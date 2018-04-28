class TruthTable:
	"""
	Representation of a truth table of all possible combinations of inputs and outputs for a given boolean expression. Boolean expressions are composed of single-character variables and operations. Expressions must be appropriately divided by brackets (e.g. 'A.B.C' must be expressed as 'A.(B.C)' or '(A.B).C'). Does not attempt to clean given expression (bar removing spaces), and may break if expression is improperly formatted. 

	Operations:
	- AND: .
	- OR: +
	- XOR: ^
	- NOT: !

	Usage:
	>>> table = TruthTable("A.B")
	>>> table
	TruthTable: expression=A.B, variables=['A', 'B'], outputs=['0', '0', '0', '1']
	>>> print(table)
	+---+---++---+
	| A | B || X |
	+---+---++---+
	| 0 | 0 || 0 |
	+---+---++---+
	| 0 | 1 || 0 |
	+---+---++---+
	| 1 | 0 || 0 |
	+---+---++---+
	| 1 | 1 || 1 |
	+---+---++---+
	>>> print(table.get_row(3))
	+---+---++---+
	| A | B || X |
	+---+---++---+
	| 1 | 1 || 1 |
	+---+---++---+
	>>> table.get_output('01')
	0
	>>> table.set_alias('A', 'Input 1')
	>>> table.set_alias('B', 'Input 2')
	>>> print(table)
	+---------+---------++---+
	| Input 1 | Input 2 || X |
	+---------+---------++---+
	|    0    |    0    || 0 |
	+---------+---------++---+
	|    0    |    1    || 0 |
	+---------+---------++---+
	|    1    |    0    || 0 |
	+---------+---------++---+
	|    1    |    1    || 1 |
	+---------+---------++---+
	"""

	def __init__(self, expression):
		"""
		Creates a new TruthTable using the given expression. The ouputs are calculated upon creation.

		Arguments:
			expression (str): boolean expression for which truth table will be created
		"""
		self.expression = expression.replace(" ", "")
		if not self._validate_expression():
			raise Exception("Invalid expression")
		self.variables = []
		self.outputs = []
		self.aliases = {}
		self._parse_expression()


	def get_row(self, row_num):
		"""
		Returns a string of the inputs and output of the given row. Rows are zero-indexed (i.e. the first row is row 0).

		e.g. For expression=A.B, row_num=3
		+---+---++---+
		| A | B || X |
		+---+---++---+
		| 1 | 1 || 1 |
		+---+---++---+

		Arguments:
			row_num (int): index of row to be retrieved
		"""
		return self._get_rows_in_range(row_num, row_num+1)


	def get_output(self, inputs):
		"""
		Returns output of boolean expression for given input string.

		Arguments:
			inputs (str): combination of bits forming input for expression. For the expression A.B, the input '01' will set A=0 and B=1. The order of inputs is determined by the order of the variables in the expression.
		"""
		if len(inputs) != len(self.variables) or inputs is None or inputs.count('0') + inputs.count('1') != len(self.variables):
			return -1
		row = int(inputs, base=2)
		return self.outputs[row]


	def set_expression(self, expression):
		"""
		Sets the boolean expression of the table to the given expression and recalculates the ouputs.

		Arguments:
			expression (str): expression to which this table's expression will be set
		"""
		self.expression = expression.replace(" ", "")
		self.outputs = []
		self._parse_expression()


	def set_alias(self, variable, alias):
		"""
		Set an alias for a variable of the expression. The alias will be displayed in place of actual variable when the table is printed.
		"""
		if alias is not None and variable is not None and variable in self.variables:
			self.aliases[variable] = alias


	def clear_aliases(self):
		"""
		Initially set the alias of each variable to be that variable (i.e. the initial 'alias' of variable 'A' is 'A').  
		"""
		for x in self.variables:
			self.aliases[x] = x


	def _parse_expression(self):
		"""
		Calculates outputs of truth table for boolean expression of this truth table.
		"""
		operations = {'.':lambda a,b: a&b, '+':lambda a,b: a|b, '^':lambda a,b: a^b}
		non_variables = list(operations.keys()) + ['(', ')', '!']
		self.variables = []
		for x in self.expression:
			if x in set(self.expression).difference(non_variables) and x not in self.variables:
				self.variables.append(x)
		self.clear_aliases()

		expression = f"({self.expression})"

		for i in range(0, 2** len(self.variables)):
			inputs = format(i, f'0{len(self.variables)}b')
			self.outputs.append(self._evaluate_expression(expression, inputs, operations))


	def _evaluate_expression(self, expression, inputs, operations):
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
			# Index of initial/opening bracketof sub-expression
			start = 0
			for i in range(0, len(expression)):
				if expression[i] == "(":
					start = i
				if expression[i] == ")":
					result = self._compute_output(expression[start:i+1], inputs, operations)
					expression[start:i+1] = result
					break
		return int(expression[0])


	def _compute_output(self, sub, inputs, operations):
		"""
		Compute result of two-variable boolean expression, being a component of some larger 
		expression (e.g. C.D in A+(B.(C.D)))

		Arguments:
			sub (list[str]): sub-expression to be evaluated
			operations (dict[str,lambda]): dictionary of boolean operations

		Returns: (str) Output of sub-expression if inputs are valid, otherwise returns -1
		"""
		# Bits to be evaluated
		results = []
		# Operation to be performed
		op = ""
		# Replace variables with appropriate bits
		for i in range(0, len(sub)):
			element = sub[i]
			if element not in (self.variables + ['0', '1']):
				op = element if element in operations.keys() else op
				continue
			result = -1
			if sub[i-1] == '!':
				r = inputs[self.variables.index(element)] if element in self.variables else sub[i]
				result = int(r)^1
			elif element in self.variables:
				result = inputs[self.variables.index(element)]
			else:
				result = element
			results.append(int(result))
		# If expression contained only single variable (e.g. 'A')
		if op == "":
			return str(results[0])
		else:
			return str(operations[op](results[0], results[1]))


	def _validate_expression(self):
		"""
		Returns true if expression is valid. A valid expression will consist only of single-character variables and valid operators (i.e. '.', '^', '+', and '!').

		Arguments:
			expression (str): expression to be validated
		"""
		return True


	def __str__(self):
		"""
		Returns an informal string representation of the thruth table, being a table-like arrangement of inputs and outputs.

		e.g. For expression=A.B:
		+---+---++---+
		| A | B || X |
		+---+---++---+
		| 0 | 0 || 0 |
		+---+---++---+
		| 0 | 1 || 0 |
		+---+---++---+
		| 1 | 0 || 0 |
		+---+---++---+
		| 1 | 1 || 1 |
		+---+---++---+
		"""
		return self._get_rows_in_range(0, len(self.outputs))


	def _get_rows_in_range(self, start, end):
		"""
		Returns an informal string representation of the rows of the truth table in the given range, being [start, end).

		e.g. For expression=A.B, start=2, end=4
		+---+---++---+
		| A | B || X |
		+---+---++---+
		| 1 | 0 || 0 |
		+---+---++---+
		| 1 | 1 || 1 |
		+---+---++---+
		"""
		# Variables to be displayed (i.e. aliases)
		display_vars = [self.aliases[x] for x in self.variables]
		# Spacing of each column based on length of each display variable
		column_spacing = [len(x) for x in display_vars]

		# Horiztonal table divider (e.g. '+---+---++---+')
		line = ""
		for x in column_spacing:
			line += "+" + ("-"*(x+2))
		line += "++---+\n"

		# Table representation, beginning with initial row of variables
		string = f"{line}| {' | '.join(display_vars)} || X |\n{line}"
		for i in range(start, end):
			# Sequence of 0s and 1s forming input 
			inputs = format(i, f'0{len(self.variables)}b')
			for j in range(0, len(display_vars)):
				# Spacings on left and right of individual input, determined by length of variable
				left_spacing = " "*(column_spacing[j]//2 + 1)
				right_spacing = " "*(len(left_spacing) - (len(display_vars[j])%2==0))
				#right_spacing = left_spacing[:len(left_spacing)-(len(display_vars[j])%2)^1]
				string += f"|{left_spacing}{inputs[j]}{right_spacing}"
			string += f"|| {self.outputs[i]} |\n{line}"
		return string[:-1]


	def __repr__(self):
		"""
		Returns a formal representation of the truth table of the form 
		'TruthTable: expression=[expression], variables=[variables], outputs=[outputs]'.
		"""
		return f"TruthTable: expression='{self.expression}', variables={self.variables}, aliases={self.aliases}, outputs={self.outputs}"


	def __eq__(self, other):
		"""
		Returns true if given truth table has same outputs as this truth table. May be used to determine equivalency of boolean expression. Two expressions are equivalent if they yield the same outputs for the same combinations of inputs (e.g. !A.!B and !(A+B) are equivalent).
		"""
		return other.outputs == self.outputs
