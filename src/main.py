from make_lexer import lex_makefile
from make_parser import parse_makefile

# Test the parser
if __name__ == "__main__":
    test_makefile = open('../tests/complex.mk').read()
    
    result = lex_makefile(test_makefile)
    print(result)