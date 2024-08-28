import ply.lex as lex

class MakeLexer:
    # List of token names
    tokens = (
        'NL', 'LEADING_TAB', 'COMMENT', 'SLIT', 'CHARS', 'VAR', 'CALL_PREFIX', 'CALL_SUFFIX',
        'ASSIGN_OP', 'OVERRIDE', 'EXPORT', 'UNEXPORT', 'IFDEF', 'IFNDEF', 'IFEQ', 'IFNEQ',
        'ELSE', 'ENDIF', 'DEFINE', 'ENDEF', 'UNDEFINE', 'INCLUDE', 'WS', 'COLON', 'COMMA'
    )

    # # Define states
    # states = (
    #     ('slcomment', 'exclusive'),
    #     ('dslit', 'exclusive'),
    #     ('sslit', 'exclusive'),
    #     ('achar', 'exclusive'),
    # )

    def __init__(self):
        self.nesting = []
        self.tab_width = 8  # Assuming tab width of 8
        self.start_tok = None
        self.start_loc = None
        self.last_returned_offset = 0
        self.fake_ws_needed = False

    def t_ASSIGN_OP(self, t):
        r'=|\?=|:=|::=|\+=|!='
        '''
        ASSIGN_OP ::= "=" | "?=" | ":=" | "::=" | "+=" | "!="
        '''
        return t
    
    
    def t_CALL_PREFIX(self, t):
        r'\$\(|\$\{'
        '''
        "$(" ::= "$(" | "${" - beginning of an expansion
        '''
        return t
    
    def t_ESCAPED_CALL_PREFIX(self, t):
        r'\$\$\('

        t.type = 'CHARS'
        self.offset += len(t.value)
        return t

    def t_ESCAPED_PAREN(self, t):
        r'\\\(|\\\)'

        t.type = 'CHARS'
        return t
    
    def t_VAR(self, t):
        r'\$.'
        return t

    def t_CALL_SUFFIX(self, t):
        r'\)|\}'
        '''
        ")" ::= ")" | "}" - ending of an expansion
        '''
        return t
    
    def t_COLON(self, t):
        r':'
        return t
    
    def t_COMMA(self, t):
        r','
        return t
    
    def t_LEADING_TAB(self, t):
        r'^\t'
        '''
        LEADING_TAB ::= <tabulation at the first position in a line (eats NL)>
        '''

        return t

    def t_WS(self, t):
        r'[ ]+'

        # We return None for WS to effectively ignore it,
        # except for LEADING_TAB which is significant
        return t

    def t_NL(self, t):
        r'[\n|\r|\r\n]+'
        # https://github.com/xaizek/zograscope/blob/master/src/make/make-lexer.flex#L122
        t.lexer.lineno += t.value.count("\n")
        
        return t

    def t_LINECONT(self, t):
        r'\\\n'
        # Line continuation is ignored
        return None

    def t_COMMENT(self, t):
        r'\#.*'
        return t

    def t_SLIT(self, t):
        r'\"[^"\n]*\"|\'[^\'\n]*\''
        return t

    # Keywords
    def t_OVERRIDE(self, t):
        r'override'
        return self.handle_keyword(t)

    def t_EXPORT(self, t):
        r'export'
        return self.handle_keyword(t)

    def t_UNEXPORT(self, t):
        r'unexport'
        return self.handle_keyword(t)

    def t_IFDEF(self, t):
        r'ifdef'
        return self.handle_keyword(t)

    def t_IFNDEF(self, t):
        r'ifndef'
        return self.handle_keyword(t)

    def t_IFEQ(self, t):
        r'ifeq'
        return self.handle_keyword(t)

    def t_IFNEQ(self, t):
        r'ifneq'
        return self.handle_keyword(t)

    def t_ELSE(self, t):
        r'else'
        return self.handle_keyword(t)

    def t_ENDIF(self, t):
        r'endif'
        return self.handle_keyword(t)

    def t_DEFINE(self, t):
        r'define'
        return self.handle_keyword(t)

    def t_ENDEF(self, t):
        r'endef'
        return self.handle_keyword(t)

    def t_UNDEFINE(self, t):
        r'undefine'
        return self.handle_keyword(t)

    def t_INCLUDE(self, t):
        r'^\s-?include'
        return self.handle_keyword(t)

    def handle_keyword(self, t):
        if not self.nesting:
            return t
        else:
            t.type = 'CHARS'
            return t

    # Special handling for nested structures and function calls
    def t_LPAREN(self, t):
        r'\('
        t.type = 'CHARS'
        if self.nesting:
            self.nesting.append('ARG')
        return t

    def t_RPAREN(self, t):
        r'\)'
        t.type = 'CHARS'
        if self.nesting:
            if self.nesting[-1] == 'ARG':
                self.nesting.pop()
            else:
                t.type = 'CALL_SUFFIX'
                self.nesting.pop()
        return t

    def t_CHARS(self, t):
        r'([-a-zA-Z0-9_/.])+|.'
        '''
        CHARS ::= <sequence of non-whitespace>
        '''
        return t

    # Error handling rule
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {self.line}, column {self.col}")
        t.lexer.skip(1)

    def t_eof(self, t):
        if self.nesting:
            print(f"Unexpected EOF in {self.nesting[-1]} block")
            return None
        return
    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Test the lexer
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


def lex_makefile(makefile_content):
    # TODO: do I need complex regular expressions rules

    lexer = MakeLexer()
    lexer.build()
    lexer.test(makefile_content)