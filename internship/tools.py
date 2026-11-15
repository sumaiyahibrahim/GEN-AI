"""Read-only tools. No email is sent and model-supplied code is never executed."""
import ast
import math
import operator

TICKETS = {
    'T-1001': {'status': 'In progress', 'category': 'Login', 'owner': 'Support team'},
    'T-1002': {'status': 'Resolved', 'category': 'Billing', 'owner': 'Accounts team'},
}


def calculate(expression):
    if not isinstance(expression, str) or len(expression) > 120:
        raise ValueError('Expression must be a string of at most 120 characters.')
    operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                  ast.Div: operator.truediv}
    def visit(node, depth=0):
        if depth > 15:
            raise ValueError('Expression nesting is too deep.')
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](visit(node.left, depth+1), visit(node.right, depth+1))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand, depth+1) * (-1 if isinstance(node.op, ast.USub) else 1)
        else:
            raise ValueError('Only numbers, parentheses, +, -, *, and / are allowed.')
        if abs(value) > 1e12 or not math.isfinite(value):
            raise ValueError('Result exceeds the allowed numeric range.')
        return value
    return visit(ast.parse(expression, mode='eval').body)


def tool_schemas():
    specs = [
        ('calculate', 'Calculate a basic arithmetic expression.', 'expression', 'Arithmetic string'),
        ('lookup_ticket', 'Look up a fictional sample support ticket.', 'ticket_id', 'Ticket ID, such as T-1001'),
        ('search_documents', 'Search the indexed support documents.', 'query', 'Search query'),
    ]
    return [{'type': 'function', 'function': {'name': name, 'description': description,
        'parameters': {'type': 'object', 'properties': {key: {'type': 'string', 'description': help_text}},
                       'required': [key], 'additionalProperties': False}}}
        for name, description, key, help_text in specs]


def execute_tool(name, arguments, kb=None):
    expected = {'calculate': 'expression', 'lookup_ticket': 'ticket_id', 'search_documents': 'query'}
    if name not in expected or not isinstance(arguments, dict) or set(arguments) != {expected[name]}:
        raise ValueError('Unknown tool or invalid arguments.')
    value = arguments[expected[name]]
    if not isinstance(value, str):
        raise ValueError('Tool argument must be text.')
    if name == 'calculate':
        return {'result': calculate(value)}
    if name == 'lookup_ticket':
        return TICKETS.get(value, {'error': 'Sample ticket not found'})
    if kb is None:
        raise ValueError('Document search requires an indexed knowledge base.')
    return kb.search(value, k=3)
