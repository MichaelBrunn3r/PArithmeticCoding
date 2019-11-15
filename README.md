## About
This small tool is supposed to help you when encoding a string with Arithmetic Coding by hand.

## Usage
`python arithmetic.py [-h] {intervals,encode}` 
Arguments:
- `{intervals,encode}`: The subcommand to run

### Subcommand Encode
Encodes the input string using Arithmetic Coding

Usage: `python arithmetic.py intervals [-h] [string] [-g] [-d]`
Arguments:
- `string`: The input string to encode. Omit to use stdin
- `-g`: The size to group the encoded string by. E.g. `-g 3`: '010 101 101 110'
- `-d`: The group delimiter. Default is ' '

### Subcommand Intervals
Outputs table of the intervals created in each step of Arithmetic Encoding.

Usage: `python arithmetic.py intervals [-h] [string] [-c] [-p]`
Arguments:
- `string`: String to create intervals from. Omit to use stdin
- `-c`: The table columns to include in that order
  - Structure: `(<column>{<options>})+`
  - `<options>`: A python dictionary with options for the column. Some options are special to one column.
    - option `name`: Custom column header
    - option `frac`: Outputs limit as a fraction instead of a decimal
    - option `f`: Format for the decimal number 
  - `<column>`:
    - `[`: The lower Interval limit
    - `]`: The upper Interval limit
    - `d`: The width/delta if the Interval
- `p`: Pretty print table using prettytable

## Examples
- Encode string:<br>
  `python arithmetic.py encode "arithmetic"`<br>
  `0001001101100100000010001101`
- Encode string, group by 4 and seperate with '.':<br>
  `python arithmetic.py encode "arithmetic" -g 4 -d '.'`<br>
  `0001.0011.0110.0100.0000.1000.1101`
- Print table of intervals:<br>
  `python arithmetic.py intervals "arithmetic"`
  ```
  a;0.0;0.1
  r;0.07;0.08
  i;0.074;0.076
  t;0.0756;0.076
  h;0.07572;0.07576
  m;0.075744;0.075748
  e;0.0757448;0.0757452
  t;0.07574512;0.0757452
  i;0.075745152;0.075745168
  c;0.0757451536;0.0757451552
  ```
- Pretty printed table with columns lower limit, upper limit and Interval width/delta:<br>
  `python arithmetic.py intervals "arithmetic" -p -c []d`
  ```
  +-------+--------------+--------------+----------+
  | Chars |    Lower     |    Upper     | Delta I  |
  +-------+--------------+--------------+----------+
  |   a   |      0       |     0.1      |   0.1    |
  |   r   |     0.07     |     0.08     |   0.01   |
  |   i   |    0.074     |    0.076     |  0.002   |
  |   t   |    0.0756    |    0.076     |  0.0004  |
  |   h   |   0.07572    |   0.07576    | 0.00004  |
  |   m   |   0.075744   |   0.075748   | 0.000004 |
  |   e   |  0.0757448   |  0.0757452   |   4E-7   |
  |   t   |  0.07574512  |  0.0757452   |   8E-8   |
  |   i   | 0.075745152  | 0.075745168  |  1.6E-8  |
  |   c   | 0.0757451536 | 0.0757451552 |  1.6E-9  |
  +-------+--------------+--------------+----------+
  ```
- Pretty printed table, columns '[]d', lower limits in fractions, upper limits with 4 decimals, renamed Interval width column:<br>
  `python arithmetic.py intervals "arithmetic" -p -c "[{'frac':True}]{'f':':.4f'}d{'name':'Width'}"`
  ```
  +-------+--------------------+--------+----------+
  | Chars |       Lower        | Upper  |  Width   |
  +-------+--------------------+--------+----------+
  |   a   |         0          | 0.1000 |   0.1    |
  |   r   |       7/100        | 0.0800 |   0.01   |
  |   i   |       37/500       | 0.0760 |  0.002   |
  |   t   |      189/2500      | 0.0760 |  0.0004  |
  |   h   |     1893/25000     | 0.0758 | 0.00004  |
  |   m   |     2367/31250     | 0.0757 | 0.000004 |
  |   e   |   94681/1250000    | 0.0757 |   4E-7   |
  |   t   |   473407/6250000   | 0.0757 |   8E-8   |
  |   i   |   591759/7812500   | 0.0757 |  1.6E-8  |
  |   c   | 47340721/625000000 | 0.0757 |  1.6E-9  |
  +-------+--------------------+--------+----------+
  ```