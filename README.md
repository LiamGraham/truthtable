# Truth Table Generator

Tool to evaluate any given boolean expression and generate a truth table of all possible inputs and outputs. truthtable.py allows the creation of a TruthTable object which stores truth table and expression data. A text-based representation of the table may be retrieved, as may individual rows. 

## Operations
- AND: &
- OR: +
- XOR: ^
- NOT: !

## Methods
- ```get_row(row_num)```
- ```get_output(inputs)```
- ```set_alias(variable, alias)```
- ```set_expression(expression)```
- ```set_alias(variable, alias)```
- ```clear_aliases()```
- ```sum_of_products()```
- ```merge(table, operator)```
- ```set_ordering(ordering)```
- ```clear_ordering()```

## Usage
```
>>> from truthtable import *
>>> table = TruthTable("A.B")
>>> table
TruthTable: expression='A.B', variables=['A', 'B'], aliases={'A': 'A', 'B': 'A'}, outputs=[0, 0, 0, 1]
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
>>> table.merge(TruthTable('A+B'), '.')
>>> table
TruthTable: expression='(A.B).(C+D)', variables=['A', 'B', 'C', 'D'], aliases={'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D'}, outputs=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
```
