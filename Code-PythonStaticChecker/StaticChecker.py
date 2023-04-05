import ast
import sys


class StaticChecker(ast.NodeVisitor):
    def __init__(self):
        self.variables = {}
        self.visited = {}
        self.isErroneous = False

    def visit_Assign(self, node):
        target = node.targets[0]
        if(target.id not in self.visited):
            self.visited[target.id] = 0
        if isinstance(target, ast.Name):
            self.variables[target.id] = self._get_type(node.value)
        self.generic_visit(node)

    def visit_Name(self, node):
        # print("#####", node.id)
        
        if isinstance(node.ctx, ast.Load) and node.id not in self.variables:
            self._report_error(node, f"Variable '{node.id}' used before assignment")
        else:
            self.visited[node.id] += 1
    

    def visit_BinOp(self, node):
        left_type = self._get_type(node.left)
        right_type = self._get_type(node.right)
        
        # print(node.left, node.right)
        if type(node.left) == ast.Name and node.left.id in self.visited:
            # print(node.left.id, self.visited[node.left.id])
            self.visited[node.left.id] += 1
            # print(node.left.id, self.visited[node.left.id])
        if type(node.right) == ast.Name and node.right.id in self.visited:
            # print(node.right.id, self.visited[node.right.id])
            self.visited[node.right.id] += 1
            # print(node.right.id, self.visited[node.right.id])
        # print("#####", left_type, right_type)
        if left_type != None and right_type != None:
            if left_type != right_type:
                self._report_error(node, f"Type mismatch: {left_type} {type(node.op).__name__} {right_type}")


        # print("#####", type(node.op), ast.Div, type(node.op) == ast.Div, node.op._attributes)
        if type(node.op) == ast.Div and type(node.right) != ast.Name and node.right.value == 0:
            # print("#####", (node.right._attributes))
            self._report_error(node, f"Division by zero")

        self.generic_visit(node)

    def _get_type(self, node):
        if isinstance(node, ast.Num):
            return "int"
        elif isinstance(node, ast.Str):
            return "str"
        elif isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            else:
                return None
        else:
            return None

    def _report_error(self, node, message):
        line = node.lineno
        col = node.col_offset
        print(f"Error at line {line}, column {col}: {message}")
        self.isErroneous = True

    def checkUnused(self):
        for i in self.visited:
            # print(i, self.visited[i])
            if self.visited[i] <= 1:
                print(f"Warning: Unused Variable {i}")

def static_check(code):
    tree = ast.parse(code)
    checker = StaticChecker()
    checker.visit(tree)



    # print((checker.visited))
    checker.checkUnused()
    if not checker.isErroneous:
        print("The python program passed Static Checking without any Errors.")

with open(sys.argv[1], 'r') as my_file:
    code = my_file.read()


# code = """
# a = 1
# d = 10
# b = 0 + z
# c = a / 0
# while b :
#     if a > 12:
#         break
#     if a < 3:
#         a = a+1/3
#         continue 
#     else:
#         continue
# """
try:
    static_check(code)
except SyntaxError as s:
    print(s)
