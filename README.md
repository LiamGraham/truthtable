# Truth Table Generator

Tool to evaluate any given boolean expression and generate a truth table of all possible inputs and outputs. truthtable.py allows the creation of a TruthTable object which stores truth table and expression data. A text-based representation of the table may be retrieved, as may individual rows. One may also retrieve the output of the expression for a given set of inputs. 

## Operations
- AND: &
- OR: +
- XOR: ^
- NOT: !

## Usage
```
>>> from truthtable import *
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
```
