import string

class TruthTable:
    """
    Representation of a truth table of all possible combinations of inputs and outputs for a given boolean expression. Boolean expressions are composed of single-character variables and operations. Expressions must be appropriately divided by brackets (e.g. 'A.B.C' must be expressed as 'A.(B.C)' or '(A.B).C') indicating precedence/order of operations.

    Operations:
    - AND: &, .
    - OR: +, |
    - XOR: ^, #
    - NOT: !, ~

    Attributes:
        expression (str): boolean expression for which table is created
        variables (list[str]): variables in expression
        outputs (list[int]): complete set of outputs of truth table
        aliases (dict[str, str]): aliases of variables to be displayed 
        operations (dict[str, lambda]): possible boolean operations and their symbols
    """

    def __init__(self, expression):
        """
        Creates a new TruthTable using the given expression. The ouputs are calculated upon creation.

        Arguments:
            expression (str): boolean expression for which truth table will be created
        """
        if expression is None:
            raise TypeError("Expression cannot be None")
        self.expression = ""
        self.variables = []
        self.outputs = []
        self.aliases = {}
        self.operations = {}
        self.functions = {}
        self.negators = []
        self._initialise_operations()
        self.set_expression(expression)


    def get_row(self, row_num):
        """
        Returns the inputs and output of the row in the truth table of the given row number. Rows are zero-indexed (i.e. the first row is row 0).

        e.g. For expression=A.B, row_num=3
        +---+---++---+
        | A | B || X |
        +---+---++---+
        | 1 | 1 || 1 |
        +---+---++---+

        Arguments:
            row_num (int): index of row to be retrieved

        Returns (str): inputs and output of row of given row number
        """
        return self._get_rows_in_range(row_num, row_num+1)


    def get_output(self, inputs):
        """
        Returns output of boolean expression for given input string.

        Arguments:
            inputs (str): combination of bits forming input for expression. For the expression A.B, the input '01' will set A=0 and B=1. The order of inputs is determined by the order of the variables in the expression.

        Returns (int): output of boolean expression for given inputs if inputs are valid, otherwise -1
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
        self._validate_expression()
        self.variables = self._parse_variables()
        self._parse_expression()
        self.clear_aliases()


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
        self.aliases.clear()
        for x in self.variables:
            self.aliases[x] = x


    def equivalent(self, expression):
        """
        Returns true if the expression of this truth table is equivalent to given expression (i.e. they both yield the same outputs).

        Returns (boolean): true if given expression is equivalent to the expression of this table
        """
        if expression != self.expression:
            table = TruthTable(expression)
        else:
            table = self
        return table == self


    def sum_of_products(self):
        """
        Returns sum of products expression for this truth table.

        e.g. The following table will return '(!A.B)+(A.!B)+(A.B)'
        +---+---++---+
        | A | B || X |
        +---+---++---+
        | 0 | 0 || 0 |
        +---+---++---+
        | 0 | 1 || 1 |
        +---+---++---+
        | 1 | 0 || 1 |
        +---+---++---+
        | 1 | 1 || 1 |
        +---+---++---+

        Returns (str): sum of products for this truth table
        """
        products = ""
        # indices of true outputs
        trues = [i for i in range(0, len(self.outputs)) if self.outputs[i]==1]

        for i, x in enumerate(trues):
            inputs = self._get_inputs(x)
            sub = ""
            for j in range(0, len(inputs)):
                sub += f"{'!'*(inputs[j]=='0')}{self.variables[j]}{'.'*(j<len(inputs)-1)}"
            products += f"({sub}){'+'*(i<(len(trues)-1))}"
        return products


    def merge(self, table, operator, distinct=True):
        """
        Merges the expression of the given truth table with this table by linking them with a single operator and recalculates the resulting outputs. If distinct is True, any variable names in table.expression also in self.expression will be replaced with variables not occuring in self.expression. Otherwise, duplicate variable symbols will be treated as referring to the same variable.

        e.g. 'A.B' and 'A+B', linked by '+', become '(A.B)+(C+D)'

        Arguments:
            table (TruthTable): table to be merged with this table
            operator (str): operator to link expressions of given table and this table
            distinct (boolean): if true, any variable names in table.expression also in self.expression will be replaced with variables not occuring in self.expression, otherwise table.expression will remain unchanged
        """
        self.set_expression(self._merging(table, operator, distinct))   


    def merged(self, table, operator, distinct=True):
        """
        Returns a truth table of the expression created by combining the expression of the given truth table with this table using a single linking operator. If distinct is True, any variable names in table.expression also in self.expression will be replaced with variables not occuring in self.expression. Otherwise, duplicate variable symbols will be treated as referring to the same variable.

        Arguments:
            table (TruthTable): table to be merged with this table
            operator (str): operator to link expressions of given table and this table
            distinct (boolean): if true, any variable names in table.expression also in self.expression will be replaced with variables not occuring in self.expression, otherwise table.expression will remain unchanged

        Returns (TruthTable): truth table of expression created by combining self.expression and table.expression linked by operator
        """
        return TruthTable(self._merging(table, operator, distinct))


    def _merging(self, table, operator, distinct=True):
        """
        Returns merged expression for both self.merge and self.merged.

        Arguments:
            table (TruthTable): table to be merged with this table
            operator (str): operator to link expressions of given table and this table
            distinct (boolean): if true, any variable names in table.expression also in self.expression will be replaced with variables not occuring in self.expression, otherwise table.expression will remain unchanged

        Raises:
            TypeError: if given table is None
            InvalidExpressionError: if given operator is not legal (i.e. operator in self.operations.keys() == False)

        Returns (str): expression created by combining self.expression and table.expression linked by operator
        """
        if type(table) != TruthTable:
            raise TypeError(f"Table must be a TruthTable, not a {type(table)}")
        if operator not in self.operations.keys():
            raise InvalidExpressionError(f"Illegal operator: {operator}")
        
        # Variables in self.expression also in table.expression
        duplicates = []
        texp = table.expression

        if distinct:
            texp = self._replace_duplicates(texp)

        return f"({self.expression}){operator}({texp})"


    def set_ordering(self, ordering):
        """
        Set order in which variables will be arranged in truth table.

        Arguments:
            ordering (list[str]): all variables in expression as they will be ordered in truth table
        """
        if ordering is None:
            raise TypeError("Ordering cannot be None")
        if set(ordering) != set(self.variables):
            raise InvalidExpressionError("Ordering must contain all variables in expression")
        self.variables = ordering
        self._parse_expression()


    def clear_ordering(self):
        """
        Remove specified ordering of variables and restore natural ordering (i.e. order in which they appear in expression).
        """
        self.variables = self._parse_variables()
        self._parse_expression()


    def add_operator(self, name, symbol):
        """
        Assign the given symbol to the function of the given name (AND, XOR, or OR). Symbol must be a single non-letter character. 

        Arguments:
            name (str): name of operator to be added (AND, XOR, or OR)
            symbol (str): symbol of operator to be added
        """
        operators = {'AND':['.', '&'], 'OR':['+', '|'], 'XOR':['^', '#']}
        if name not in ['AND', 'OR', 'XOR']:
            raise InvalidExpressionError("Name must be AND, OR, or XOR")
        if len(symbol) != 1 or symbol in string.ascii_letters:
            raise InvalidExpressionError("Symbol must be a single non-letter character")
        for op in operators:
            if symbol in operators[op]:
               raise InvalidExpressionError(f"'{symbol}' is already an operator") 

        self.operations[symbol] = self.functions[name]



    def _replace_duplicates(self, expression):
        # Variables in self.expression also in table.expression
        duplicates = []
        
        for x in expression:
            if x in string.ascii_letters and x in self.expression:
                duplicates.append(x)
        
        # Available variables that may replace duplicate variables in table.expression
        available = iter(sorted(set(string.ascii_uppercase).difference(set(self.expression).intersection(string.ascii_letters))))

        for x in duplicates:
            expression = expression.replace(x, next(available))
        return expression


    def _parse_expression(self):
        """
        Calculates outputs of truth table for boolean expression of this truth table.
        """
        self.outputs = []
        self.clear_aliases()

        expression = f"({self.expression})"

        for i in range(0, 2**len(self.variables)):
            inputs = self._get_inputs(i)
            self.outputs.append(self._evaluate_expression(expression, inputs))


    def _parse_variables(self):
        non_variables = list(self.operations.keys()) + ['(', ')', '!']
        variables = []
        for x in self.expression:
            if x in set(self.expression).difference(non_variables) and x not in variables:
                variables.append(x)
        return variables


    def _evaluate_expression(self, expression, inputs):
        """
        Evaluate given boolean expression for some combination of inputs. 

        Arguments:
            expression (str): boolean expression to be evaluated
            variables (list[str]): list of variables in complete expression
            inputs (str): binary string, with each bit being the input for the variable
            at the same index in 'variables' 
        
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
                    result = self._compute_output(expression[start:i+1], inputs)
                    expression[start:i+1] = result
                    break
        return int(expression[0])


    def _compute_output(self, sub, inputs):
        """
        Compute result of two-variable boolean expression, being a component of some larger 
        expression (e.g. C.D in A+(B.(C.D)))

        Arguments:
            sub (list[str]): sub-expression to be evaluated

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
                op = element if element in self.operations.keys() else op
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
            return str(self.operations[op](results[0], results[1]))


    def _validate_expression(self):
        """
        Determines if expression is valid. A valid expression will consist only of single-character variables and valid operators (i.e. '.', '^', '+', and '!'). The order of operations will be appropriately defined by closed parentheses.

        Invalid Expressions:
        - A.
        - A.(B+C
        - A!.B
        """
        self._check_bracket_closure()
        self._check_symbols()
        self._check_precedence()


    def _check_symbols(self):
        """
        Determine if non-parathetic symbols are legal (i.e. letters or operators) and are in a valid order (i.e. operators precede and follow variables, and vice versa).

        Raises:
            InvalidExpressionError: if 
        """
        message = ""
        prev = "\n"
        expression = self.expression.replace("(", "").replace(")", "")

        for i in range(0, len(expression)):
            char = expression[i]
            if char in self.operations.keys() and (prev not in string.ascii_letters or i == (len(expression) - 1)):
                message = f"Operator must occur between variables or subexpressions ({i})"
                break
            elif char in string.ascii_letters and i > 0 and prev != '!' and prev not in self.operations.keys():
                message = f"Variable must precede or follow an operator ({i})"
                break
            elif char == '!' and ((prev not in self.operations.keys() and i > 0) or (i == (len(expression) - 1))):
                message = f"Negator must precede a variable {'and follow an operator '*(i>0)}({i})"
            elif char != '!' and char not in self.operations.keys() and char not in string.ascii_letters:
                message = f"Invalid symbol in expression: {char} ({i})"
                break
            prev = char
        if message or not expression:
            message += "Expression must contain variables and operators"*(len(expression)==0)
            raise InvalidExpressionError(message)


    def _check_bracket_closure(self):
        """
        Determine if expression brackets are properly matched.

        e.g. 'A.(B+C)' is valid, 'A.(B+C' is not

        Raises:
            InvalidExpressionError: if brackets are improperly matched
        """
        # Open brackets increment, closed brackets decrement, valid expression has closure of 0
        closure = 0
        change = {'(':1, ')':-1}
        for x in self.expression:
            closure += change.get(x, 0)
            if closure < 0:
                break
        if closure != 0:
            raise InvalidExpressionError("Brackets are improperly matched")


    def _check_precedence(self):
        """
        Determine if order of operations is clearly indicated by paratheses. An expression must contain only of parathesised subexpressions consisting of two variables (or subexpressions) and one operator. The outermost subexpression need not be parenthesised.

        e.g. A.(B+C) is valid, A.B+C is not 

        Raises:
            InvalidExpressionError: if precendence/order of operations is not properly indicated

        """
        expression = list(f"({self.expression})")
        while len(expression) > 1:
            for i in range(0, len(expression)):
                if expression[i] == "(":
                    start = i
                if expression[i] == ")":
                    sub = expression[start+1:i]
                    # Sub-expression contains 3 characters (2 variables and 1 operator) + any negators that might be present
                    if len(sub) > (3+sub.count("!")):
                        raise InvalidExpressionError("Order of operations unclear")
                    expression[start:i+1] = "X"
                    break


    def _get_inputs(self, value):
        """
        Returns sequence of bits together forming input for boolean expression, whereby the corresponding variable of each bit is self.variables[index of current bit].

        Arguments:
            value (int): base-10 (decimal) value to be converted to binary input sequence

        Returns (str): sequence of bits forming input
        """
        return format(value, f'0{len(self.variables)}b')


    def __str__(self):
        """
        Returns an informal string representation of the truth table, being a table-like arrangement of inputs and outputs.

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

        Returns (str): informal representation of truth table
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

        Returns: informal string representation of rows of truth table in given range
        """
        # Variables to be displayed (i.e. aliases)
        display_vars = [self.aliases[x] for x in self.variables]
        # Spacing of each column based on length of each display variable
        column_spacing = []

        # Horiztonal table divider (e.g. '+---+---++---+')
        line = ""
        for x in display_vars:
            line += "+" + ("-"*(len(x)+2))
        line += "++---+\n"

        for i in range(0, len(display_vars)):
            # Spacings on left and right of individual input, determined by length of alias
            left_spacing = " "*(len(display_vars[i])//2 + 1)
            right_spacing = " "*(len(left_spacing) - (len(display_vars[i])%2==0))
            column_spacing.append((left_spacing, right_spacing))

        # Table representation, beginning with initial row of variables
        string = f"{line}| {' | '.join(display_vars)} || X |\n{line}"
        for i in range(start, end):
            # Sequence of 0s and 1s forming input 
            inputs = self._get_inputs(i)
            for j in range(0, len(display_vars)):
                string += f"|{column_spacing[j][0]}{inputs[j]}{column_spacing[j][1]}"
            string += f"|| {self.outputs[i]} |\n{line}"
        return string[:-1]


    def _initialise_operations(self):
        """
        Bind the default legal operators to the appropriate functions.
        """
        self.functions = {'AND':lambda a,b: a&b, 'OR':lambda a,b: a|b, 'XOR':lambda a,b: a^b}
        operators = {'AND':['.', '&'], 'OR':['+', '|'], 'XOR':['^', '#']}

        for op in operators:
            for symb in operators[op]:
                self.operations[symb] = self.functions[op]


    def __repr__(self):
        """
        Returns a formal representation of the truth table of the form 
        'TruthTable: expression=[expression], variables=[variables], outputs=[outputs]'.

        Returns (str): formal representation of truth table
        """
        return f"TruthTable: expression='{self.expression}', variables={self.variables}, aliases={self.aliases}, outputs={self.outputs}"


    def __eq__(self, other):
        """
        Returns true if given truth table has same outputs as this truth table. May be used to determine equivalency of boolean expression. Two expressions are equivalent if they yield the same outputs for the same combinations of inputs (e.g. !A.!B and !(A+B) are equivalent).

        Returns (boolean): true if outputs of given truth table equal outputs of this truth table
        """
        return other.outputs == self.outputs


class InvalidExpressionError(Exception):

    def __init__(self, message):
        self.message = message


if __name__ == "__main__":
    import sys
    try:
        print(TruthTable(sys.argv[1]))
    except IndexError:
        pass
