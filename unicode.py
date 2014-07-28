"""
Pylint plugin to deal with the following rules:

1) allow only unicode string literals
2) implement __unicode__ instead of __str__
3) Mark the % operator as deprecated. Prefer unicode.format
"""

import tokenize
from pylint.checkers import BaseTokenChecker, BaseChecker
from pylint.interfaces import ITokenChecker, IRawChecker, IAstroidChecker


class ImplementUnicodeMagicMethod(BaseChecker):
    __implements__ = (IAstroidChecker,)
    name = 'unicode-magic-method'
    msgs = {
        'W1405': ('Implement __unicode__ instead of __str__',
                  'implement-unicode-magic-method',
                  'Used when a __str__ method is detected instead of a __unicode__')
    }

    def visit_function(self, node):
        if node.name == '__str__' and not [n for n in node.parent.values() if n.name == '__unicode__']:
            self.add_message('implement-unicode-magic-method', node=node.parent)


class StringFormatDeprecated(BaseChecker):
    __implements__ = (IAstroidChecker,)

    name = 'string-format-deprecated'

    msgs = {
        'W1404': ('% operator is deprecated',
                  'string-format-operator-deprecated',
                  'Used when a string format operator is detected')
    }

    def visit_binop(self, node):
        if node.op == '%':
            if isinstance(node.left.value, basestring):
                self.add_message('string-format-operator-deprecated', node=node)


class OnlyUnicodeChecker(BaseTokenChecker):
    __implements__ = (ITokenChecker, IRawChecker)

    name = 'only_unicode'

    msgs = {
        'W1403': ('simple string literal detected. Use r or u prefix',
                  'simple-basestring-literal',
                  'Used when a basestring literal is detected'),
    }

    def process_module(self, module):
        pass

    def process_tokens(self, tokens):
        previous_token = None
        for (tok_type, token, (start_row, start_col), _, _) in tokens:
            if tok_type in (tokenize.INDENT, tokenize.NEWLINE, tokenize.COMMENT) or token == '\n':
                continue
            if tok_type == tokenize.STRING:
                if previous_token and previous_token[1] != ':':  # skip docstrings
                    self.process_string_token(token, start_row, start_col)
            previous_token = (tok_type, token)

    def process_string_token(self, token, start_row, start_col):
        for i, c in enumerate(token):
            if c in '\'\"':
                break
        markers = token[:i].lower()
        if 'r' and 'u' not in markers:
            self.add_message('simple-basestring-literal', line=start_row)


def register(linter):
    """required method to auto register this checker """
    linter.register_checker(OnlyUnicodeChecker(linter))
    linter.register_checker(StringFormatDeprecated(linter))
    linter.register_checker(ImplementUnicodeMagicMethod(linter))
