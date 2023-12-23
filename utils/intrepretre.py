from datetime import datetime

STRING = 'string'

class Interpreter:
    def __init__(self, path: str):
        self.file = open(path, 'r')

        self.logging = True
        self.tokens = list()

    def log(self, *message: str):
        """ Logs `message` if `self.logging == True` """

        if not self.logging:
            return

        now = datetime.now()
        message = '\t'.join(map(str, message))
        print(f'{now} :: {message}')

    def run_token(self, token: tuple):
        ...

    def flush_tokens(self):
        """ Evaluate the token and substantially runs the tokens """
        while self.tokens and isinstance(self.tokens[0], tuple):
            self.run_token(self.tokens.pop(0))

    def is_tokenizing(self):
        """
        Return false if there's no tokens working on.
        Else, return the type of working token.
        """
        if self.tokens and isinstance(self.tokens[-1], list):
            return self.tokens[-1][0]
        return False

    def run_line(self, line: str):
        """ Tokenize the line """

        for char in line:
            if token_type := self.is_tokenizing():
                if token_type == STRING:
                    if char == '"':
                        self.tokens[-1] = tuple(self.tokens[-1])
                    else:
                        self.tokens[-1][1] += char
            else:
                if char == '"':
                    self.tokens.append([STRING, ''])

        self.log(self.tokens)

    def run(self):
        """ Runs all line in the file """

        while line := self.file.readline():
            self.run_line(line.strip())
            self.flush_tokens()

    def close(self):
        self.file.close()


if __name__ == '__main__':
    from sys import argv

    interpreter = Interpreter(argv[1])
    interpreter.run()
    interpreter.close()

