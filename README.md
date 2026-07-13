# ast-explore

Tool for exploring the AST of given Python source code.

## Installation

This package is available on PyPI. To use it, you can either install with `pip`:

```shell
pip install ast-explore
```

or use it with `uv` directly:

```shell
uvx ast-explore --help
```

## Usage

At a minimum, you must provide a Python file to analyze:

```shell
# previously-installed with pip:
ast-explore source_code.py

# with uv:
uvx ast-explore source_code.py
```

This will extract all possible data points from every node in the AST generated from that source code and print it to the screen. You may wish to pipe the results to a file or `less` to process.

Here's a partial example of the output:

```
📖 Reading Python source code from /.../source_code.py...
🔍 Parsing into a Python 3.14 AST...
✅ Ready to explore the AST! Starting depth-first traversal...

********************************************************************************
**    1. Module (https://docs.python.org/3.14/library/ast.html#ast.Module)    **
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module

📍 This node type does not have any line number information.

📝 Docstring is missing.

✨ AST node-specific fields and their values:
   - body         : [FunctionDef(n...ype_params=[])]
   - type_ignores : []

********************************************************************************
 2. FunctionDef (https://docs.python.org/3.14/library/ast.html#ast.FunctionDef)
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module -> FunctionDef

🐍 Source code represented by the node:
   1 | def strip_password(x: dict[str, str]) -> None:
   2 |     try:
   3 |         del x['password']
   4 |     except KeyError:
   5 |         pass

📍 Location in the source code:
   - lineno         : 1
   - end_lineno     : 5
   - col_offset     : 0
   - end_col_offset : 12

📝 Docstring is missing.

✨ AST node-specific fields and their values:
   - name           : 'strip_password'
   - args           : arguments(pos..., defaults=[])
   - body           : [Try(body=[Del... finalbody=[])]
   - decorator_list : []
   - returns        : Constant(value...ne, kind=None)
   - type_comment   : None
   - type_params    : []

********************************************************************************
   3. arguments (https://docs.python.org/3.14/library/ast.html#ast.arguments)
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module -> FunctionDef -> arguments

📍 This node type does not have any line number information.

✨ AST node-specific fields and their values:
   - posonlyargs : []
   - args        : [arg(arg='x', ..._comment=None)]
   - vararg      : None
   - kwonlyargs  : []
   - kw_defaults : []
   - kwarg       : None
   - defaults    : []

********************************************************************************
**       4. arg (https://docs.python.org/3.14/library/ast.html#ast.arg)       **
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module -> FunctionDef -> arguments -> arg

🐍 Source code represented by the node:
   1 | def strip_password(x: dict[str, str]) -> None:
     |                    ^^^^^^^^^^^^^^^^^

📍 Location in the source code:
   - lineno         : 1
   - end_lineno     : 1
   - col_offset     : 19
   - end_col_offset : 36

✨ AST node-specific fields and their values:
   - arg          : 'x'
   - annotation   : Subscript(val...), ctx=Load())
   - type_comment : None
```

### Specifying nodes of interest

Use the `--types` argument to list the nodes you want to explore and only information about those nodes will be shown. Here, we only care about function definition nodes:

```shell
# previously-installed with pip:
ast-explore source_code.py --types FunctionDef AsyncFunctionDef

# with uv:
uvx ast-explore source_code.py --types FunctionDef AsyncFunctionDef
```

Here's an example of the result (there are no async functions in the file analyzed):

```
📖 Reading Python source code from /.../source-code.py...
🔍 Parsing into a Python 3.14 AST...
✅ Ready to explore the AST! Starting depth-first traversal...

********************************************************************************
 1. FunctionDef (https://docs.python.org/3.14/library/ast.html#ast.FunctionDef)
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module -> FunctionDef

🐍 Source code represented by the node:
   1 | def strip_password(x: dict[str, str]) -> None:
   2 |     try:
   3 |         del x['password']
   4 |     except KeyError:
   5 |         pass

📍 Location in the source code:
   - lineno         : 1
   - end_lineno     : 5
   - col_offset     : 0
   - end_col_offset : 12

📝 Docstring is missing.

✨ AST node-specific fields and their values:
   - name           : 'strip_password'
   - args           : arguments(pos..., defaults=[])
   - body           : [Try(body=[Del... finalbody=[])]
   - decorator_list : []
   - returns        : Constant(value...ne, kind=None)
   - type_comment   : None
   - type_params    : []

********************************************************************************

🏆 Traversal completed!
```

> [!TIP]
> To exclude specific node types instead (for example, if you aren't sure yet, which type you want), use `--skip` instead of `--types`.

### Interactive mode

Use interactive mode to step through the AST one node at a time:

```shell
# previously-installed with pip:
ast-explore source_code.py --interactive

# with uv:
uvx ast-explore source_code.py --interactive
```

Here's what that looks like:

```
📖 Reading Python source code from /.../source_code.py...
🔍 Parsing into a Python 3.14 AST...
✅ Ready to explore the AST! Starting depth-first traversal...

********************************************************************************
**    1. Module (https://docs.python.org/3.14/library/ast.html#ast.Module)    **
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module

📍 This node type does not have any line number information.

❓ Do you want more information on this node? [y]es [n]o [q]uit:
```

Of course, you can combine `--interactive` with `--types` to customize your exploration. Here we interactively visit all `try` blocks:

```shell
# previously-installed with pip:
ast-explore source_code.py --interactive --types Try

# with uv:
uvx ast-explore source_code.py --interactive --types Try
```

Note that the first node we encounter is now the `ast.Try` node and not the `ast.Module` node we saw without specifying `--types`:

```
📖 Reading Python source code from /.../source_code.py...
🔍 Parsing into a Python 3.14 AST...
✅ Ready to explore the AST! Starting depth-first traversal...

********************************************************************************
**       1. Try (https://docs.python.org/3.14/library/ast.html#ast.Try)       **
********************************************************************************

🌲 Path to this node from the root node of the AST:
   Module -> FunctionDef -> Try

🐍 Source code represented by the node:
   2 |     try:
   3 |         del x['password']
   4 |     except KeyError:
   5 |         pass

❓ Show location fields? [y]es [n]o [q]uit: y

📍 Location in the source code:
   - lineno         : 2
   - end_lineno     : 5
   - col_offset     : 4
   - end_col_offset : 12

❓ Do you want more information on this node? [y]es [n]o [q]uit: y

✨ AST node-specific fields and their values:
   - body      : [Delete(target..., ctx=Del())])]
   - handlers  : [ExceptHandler...body=[Pass()])]
   - orelse    : []
   - finalbody : []

❓ Continue traversal? [y]es [n]o [q]uit:
```
