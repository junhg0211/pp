import re
from datetime import datetime
from pprint import pprint
from typing import Tuple, Optional

KEYWORD = 'keyword'
VARIABLE = 'variable'
LOCAL = 'local'

TEXT = 'text'
BOOLEAN = 'bool'
ZAHLEN = 'zahlen'
REAL = 'real'

PLUS = ['+', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
MINUS = ['-', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
MULTIPLY = ['*', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
DIVIDE = ['/', 2, (ZAHLEN, 0), (ZAHLEN, 1)]
MODULO = ['%', 2, (ZAHLEN, 0), (ZAHLEN, 1)]

LESS_THAN = ['<', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
GREATER_THAN = ['>', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
EQUALS = ['=', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
LESS_OR_EQUALS = ['<=', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
GREATER_OR_EQUALS = ['>=', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
NOT_EQUALS = ['!=', 2, (ZAHLEN, 0), (ZAHLEN, 0)]
AND = ['&', 2, (BOOLEAN, False), (BOOLEAN, False)]
OR = ['|', 2, (BOOLEAN, False), (BOOLEAN, False)]

SET = ['set', 2, (VARIABLE, '_'), None]
IF = ['if', 1.0, (BOOLEAN, False)]
ELF = ['elf', 1.0, (BOOLEAN, False)]
ELSE = ['else', 0.0]
WHILE = ['while', 1.0, (BOOLEAN, False)]
FOR = ['for', 4.0, (VARIABLE, '_'), (ZAHLEN, 0), (ZAHLEN, 0), (ZAHLEN, 1)]
WITH = ['with', 2, (LOCAL, '_'), None]

WORD = ['word', 1, (KEYWORD, 'word')]
CLASS = ['class', 1.0, (WITH, (LOCAL, '_'), (ZAHLEN, 0))]
FUNCTION = ['function', 0.0]

OF = ['of', 2, ('_', ['_', (ZAHLEN, 0)]), (VARIABLE, '_')]

tokens = {promise[0]: promise for promise in (
    PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, LESS_THAN, GREATER_THAN, EQUALS, LESS_OR_EQUALS, GREATER_OR_EQUALS,
    NOT_EQUALS, AND, OR, OF, SET, IF, ELF, ELSE, WHILE, FOR, WITH, WORD, CLASS, FUNCTION)}

zahlen_expression = re.compile(r'^-?\d+$')
real_expression = re.compile(r'^-?\d+\.\d+$')
bool_expression = re.compile(r'^(true|false)$')


def set_return_value(function):
    def decorated(self_, token, local_variables: Optional[dict] = None):
        return_value = function(self_, token, local_variables)
        if local_variables is not None:
            local_variables['RETURN'] = return_value
        return return_value

    return decorated


class Interpreter:
    def __init__(self, path: str):
        self.path = path
        self.file = open(self.path, 'r')
        self.tokens = [None]

        self.variables = dict()
        self.logging = False

        self.message_tray = list()

    def get_working(self, working=None, parent=None, index=None) -> Tuple[list, list, int]:
        if not working:
            working = self.tokens
        for i, value in enumerate(working):
            if isinstance(value, list):
                return self.get_working(value, working, i)
        return working, parent, index

    def tokenize_line(self, line: str):
        while line:
            working, working_parent, working_index = self.get_working()
            if working[0] == TEXT:
                if line[0] != '"':
                    working[1] += line[0]
                else:
                    working_parent[working_index] = tuple(working)
                line = line[1:]
            elif working[0] == KEYWORD:
                if line[0] != ' ':
                    if line[0] == '!':
                        line = ' ' + line
                    else:
                        working[1] += line[0]
                        line = line[1:]
                else:
                    if working_parent[0] == WORD[0]:
                        working_parent[working_index] = tuple(working)
                    elif working[1] in tokens:
                        working[:2] = [working[1]]
                    elif working[1] in self.variables:
                        value = self.variables[working[1]]
                        if isinstance(value, tuple) and value[0] == WORD[0]:
                            if working_parent[0] not in (WITH[0], OF[0]):
                                working[1] = value[1]
                                continue
                            else:
                                working[0] = VARIABLE
                                working_parent[working_index] = tuple(working)
                        elif isinstance(value, tuple) and value[0] == CLASS[0]:
                            if len(working) >= 3:
                                working[0] = VARIABLE
                                working_parent[working_index] = tuple(working)
                            else:
                                working[:2] = [working[1]]
                        elif isinstance(value, tuple) and value[0] == FUNCTION[0]:
                            working[:2] = [working[1]]
                        else:
                            working[0] = VARIABLE
                            working_parent[working_index] = tuple(working)
                    elif re.fullmatch(zahlen_expression, working[1]):
                        working[0] = ZAHLEN
                        working_parent[working_index] = tuple(working)
                    elif re.fullmatch(real_expression, working[1]):
                        working[0] = REAL
                        working_parent[working_index] = tuple(working)
                    elif re.fullmatch(bool_expression, working[1]):
                        working[0] = BOOLEAN
                        working_parent[working_index] = tuple(working)
                    else:
                        working[0] = VARIABLE
                        working_parent[working_index] = tuple(working)
                    line = line[1:]
            else:
                if line[0] == '"':
                    working.append([TEXT, ""])
                    line = line[1:]
                elif line[0] == ' ':
                    line = line[1:]
                elif line[0] == '!':
                    if working[0] in (IF[0], ELF[0], ELSE[0], WHILE[0], FOR[0], CLASS[0]):
                        working_parent[working_index] = tuple(working)
                        if working[0] in (IF[0], WHILE[0], FOR[0], CLASS[0]):
                            line = line[1:]
                    elif working[0] == FUNCTION[0]:
                        if len(working) <= 1 or working[1][0] == VARIABLE:
                            working.append(tuple(working[1:]))
                            working[1:-1] = []
                        else:
                            working.append(tuple(working[2:]))
                            working[2:-1] = []
                            working_parent[working_index] = tuple(working)
                        line = line[1:]
                    elif working[0] == WITH[0]:
                        working += [None]
                        working_parent[working_index] = tuple(working)
                        line = line[1:]
                    elif working[0] in self.variables and (value := self.variables[working[0]])[0] == CLASS[0]:
                        working = working + list(map(lambda x: x[1], value[1][len(working) - 1:]))
                        working_parent[working_index] = tuple(working)
                        line = line[1:]
                    elif working[0] in self.variables and (value := self.variables[working[0]])[0] == FUNCTION[0]:
                        working = working + [(ZAHLEN, 0)] * (len(value[1]) - len(working) + 1)
                        working_parent[working_index] = tuple(working)
                        line = line[1:]
                    else:
                        if working[0] is not None:
                            working = working + tokens[working[0]][2 + len(working) - 1:]
                        line = line[1:]
                else:
                    working.append([KEYWORD, line[0]])
                    line = line[1:]
            while True:
                if working[0] in tokens:
                    if isinstance(tokens[working[0]][1], int):
                        if len(list(filter(lambda x: any((isinstance(x, tuple), isinstance(x, str), x is None)),
                                           working))) >= tokens[working[0]][1] + 1:
                            working_parent[working_index] = tuple(working)
                elif working[0] in self.variables:
                    value = self.variables[working[0]]
                    if value[0] == CLASS[0]:
                        if len(list(filter(lambda x: any((isinstance(x, tuple), isinstance(x, str), x is None)),
                                           working))) >= len(value[1]) + 1:
                            working_parent[working_index] = tuple(working)
                    elif value[0] == FUNCTION[0]:
                        if len(list(filter(lambda x: any((isinstance(x, tuple), isinstance(x, str), x is None)),
                                           working))) >= len(value[1]) + 1:
                            working_parent[working_index] = tuple(working)
                previous_working = working
                working, working_parent, working_index = self.get_working()
                if previous_working == working:
                    break

    def match_type(self, a, b, ok=False):
        if a is None:
            if isinstance(b, int) or b is None:
                a = 0
            elif isinstance(b, bool):
                a = False
            elif isinstance(b, str):
                a = ''
            elif isinstance(b, float):
                a = 0.0
        elif isinstance(a, str):
            b = str(b)

        if ok:
            return a, b
        else:
            b, a = self.match_type(b, a, True)[::-1]
            return b, a

    @set_return_value
    def interpret_value(self, token, local_variables: Optional[dict] = None):
        if local_variables is None:
            local_variables = dict()
        else:
            local_variables = local_variables.copy()
        self.log('value token', token, self.variables, local_variables)
        # VALUES
        if token is None:
            return None
        elif token[0] == ZAHLEN:
            return int(token[1])
        elif token[0] == TEXT:
            return token[1]
        elif token[0] == BOOLEAN:
            return token[1] == 'true'
        elif token[0] == REAL:
            return float(token[1])

        # VARIABLES
        elif token[0] == VARIABLE:
            if token[1] in local_variables:
                return local_variables[token[1]]
            return self.variables[token[1]]
        elif token[0] == OF[0]:
            instance = self.interpret_value(token[1], local_variables)
            if token[2][0] != VARIABLE:
                raise ValueError('2nd place of OF must be a variable namespace')
            for with_ in instance[1:]:
                if with_[0] == token[2][1]:
                    return with_[1]
            raise AttributeError(f'no attribute named {token[2][1]} in {instance[0]}')

        # OPERATIONS
        elif token[0] == PLUS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a + b
        elif token[0] == MINUS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a - b
        elif token[0] == MULTIPLY[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a * b
        elif token[0] == DIVIDE[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a / b
        elif token[0] == MODULO[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a % b
        elif token[0] == LESS_THAN[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a < b
        elif token[0] == GREATER_THAN[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a > b
        elif token[0] == EQUALS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a == b
        elif token[0] == LESS_OR_EQUALS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a <= b
        elif token[0] == GREATER_OR_EQUALS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a >= b
        elif token[0] == NOT_EQUALS[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a != b
        elif token[0] == AND[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a and b
        elif token[0] == OR[0]:
            a, b = self.match_type(self.interpret_value(token[1], local_variables),
                                   self.interpret_value(token[2], local_variables))
            return a or b

        # GENERATORS
        elif token[0] == WORD[0]:
            if token[1][0] != KEYWORD:
                raise ValueError('2nd place of WORD value must be a keyword namespace')
            return WORD[0], token[1][1]
        elif token[0] == CLASS[0]:
            withs = list()
            for subtoken in token[1:]:
                if subtoken[0] != WITH[0]:
                    raise ValueError('only WITH promise can come in the class declaration')
                if subtoken[1][0] != VARIABLE:
                    raise ValueError('2nd place of HAVING must be a variable namespace')
                withs.append([subtoken[1][1], self.interpret_value(subtoken[2], local_variables)])
            return CLASS[0], withs
        elif token[0] == FUNCTION[0]:
            parameters = tuple(map(lambda x: x[1], token[1]))
            promises = token[2]
            return FUNCTION[0], parameters, promises
        # CUSTOM GENERATORS
        elif token[0] in local_variables or token[0] in self.variables:
            value = self.variables[token[0]]
            if token[0] in local_variables:
                value = local_variables[token[0]]
            if value[0] == CLASS[0]:
                result = [token[0]]
                for i, subtoken in enumerate(token[1:]):
                    key = value[1][i][0]
                    value_ = self.interpret_value(subtoken, local_variables)
                    result.append([key, value_])
                return result
            elif value[0] == FUNCTION[0]:
                local_variables = {value[1][i]: self.interpret_value(token[i + 1], local_variables)
                                   for i in range(len(token) - 1)}
                local_variables['RETURN'] = None
                for promise in value[2]:
                    self.run_promise(promise, local_variables)
                return local_variables['RETURN']

        raise ValueError(f'{token} is not a value type')

    def set_variable(self, name: str, value):
        self.variables[name] = value
        if name == 'message':
            self.message_tray.append(value)

    def flush(self):
        result = self.message_tray
        self.message_tray = list()
        return result

    def run_promise(self, token: Optional[tuple], local_variables: Optional[dict] = None):
        if token[0] == SET[0]:
            if token[1][0] == VARIABLE:
                name = token[1][1]
                value = self.interpret_value(token[2], local_variables)
                if local_variables is None:
                    self.set_variable(name, value)
                else:
                    local_variables[name] = value
                self.log(token, f'set {name} = {value}', self.variables)
            elif token[1][0] == OF[0]:
                of = self.interpret_value(token[1][1])
                name = token[1][2][1]
                value = self.interpret_value(token[2])
                for local_variable in of:
                    if local_variable[0] == name:
                        local_variable[1] = value
                self.log(token, f'set {of}[{name}] = {value}', self.variables)
        elif token[0] in (IF[0], ELF[0]):
            condition = self.interpret_value(token[1], local_variables)
            self.log(token, '...', condition)
            if condition:
                for subtoken in token[2:]:
                    if subtoken[0] not in (ELF[0], ELSE[0]):
                        self.run_promise(subtoken, local_variables)
            else:
                for subtoken in token[2:]:
                    if subtoken[0] in (ELF[0], ELSE[0]):
                        self.run_promise(subtoken, local_variables)
        elif token[0] == ELSE[0]:
            self.log(token)
            for subtoken in token[1:]:
                self.run_promise(subtoken, local_variables)
        elif token[0] == WHILE[0]:
            self.log(token)
            while self.interpret_value(token[1]):
                for subtoken in token[2:]:
                    self.run_promise(subtoken, local_variables)
        elif token[0] == FOR[0]:
            self.log(token)
            for i in range(self.interpret_value(token[2], local_variables),
                           self.interpret_value(token[3], local_variables),
                           self.interpret_value(token[4], local_variables)):
                self.run_promise((SET[0], token[1], (ZAHLEN, i)), local_variables)
                for subtoken in token[5:]:
                    self.run_promise(subtoken, local_variables)
        else:
            return self.interpret_value(token, local_variables)

    def tick(self):
        if line := self.file.readline():
            self.tokenize_line(line.strip() + ' ')
            self.log('line token', self.tokens)
            while len(self.tokens) > 1 and isinstance(self.tokens[1], tuple):
                self.run_promise(self.tokens[1])
                del self.tokens[1]
            return 0
        else:
            return 1

    def run(self):
        while not self.tick():
            pass
        self.close()

    def log(self, *message):
        if self.logging:
            now = datetime.now()
            print(now, *message, sep='\t')

    def close(self):
        self.file.close()
        if len(self.tokens) > 1:
            raise EOFError


if __name__ == '__main__':
    interpreter = Interpreter('out/untitled.ppp')
    interpreter.logging = True
    interpreter.run()
    pprint(interpreter.variables)

