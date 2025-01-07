#analisador sintático
import ply.yacc as yacc

# Get the token map from the lexer.  This is required
from owl2lex import tokens, lexer
# tokens: ['IDENTIFIER', 'INDIVIDUAL', 'PROPERTY', 'INTEGER', 'SPECIAL', 'TYPE', 'SOME', 'ALL', 'VALUE', 'MIN', 'MAX', 'EXACTLY', 'THAT', 'NOT', 'AND', 'OR', 'CLASS', 'EQUIVALENTO', 'INDIVIDUALS', 'SUBCLASSOF', 'DISJOINTCLASSES']

# Precedência dos operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'SOME', 'ALL', 'VALUE', 'MIN', 'MAX', 'EXACTLY', 'THAT', 'NOT'),
)

# Regras da gramática

def p_class_declaration(p):
    """class_declaration : CLASS IDENTIFIER class_body"""
    p[0] = ('ClassDeclaration', p[2], p[3])

def p_class_body(p):
    """class_body : primitive_body
                  """
    p[0] = ('ClassBody', p[1:])

def p_class_body_error(p):
    """class_body : error"""
    print('Erro de sintaxe na declaração de classe')

def p_primitive_body(p):
    """primitive_body : subclass_section disjoint_section individuals_section
                   | subclass_section disjoint_section
                   | subclass_section individuals_section
                   | subclass_section
                      """
    print('classe primitiva: ', p[1:])
    p[0] = ('ClassBody', p[1])

#classe definida
def p_defined_body(p):
    """defined_body : equivalent_section disjoint_section individuals_section
                   | equivalent_section disjoint_section
                   | equivalent_section individuals_section
                   | equivalent_section
                      """
    print('classe definida: ', p[1:])
    p[0] = ('ClassBody', p[1])

#corpo de Classe com axioma de fechamento (closure axiom)
def p_closure_body(p):
    """closure_body : subclass_section_only disjoint_section individuals_section
                     | subclass_section_only disjoint_section
                     | subclass_section_only individuals_section
                     | subclass_section_only
                      """
    print('classe com axioma de fechamento: ', p[1:])
    p[0] = ('ClassBody', p[1])

#corpo de classe com  Classe com descrições aninhadas
def p_nested_body(p):
    """nested_body : equivalent_section_nested disjoint_section individuals_section
                     | equivalent_section_nested disjoint_section
                     | equivalent_section_nested individuals_section
                     | equivalent_section_nested
                      """
    print('classe com descrições aninhadas: ', p[1:])
    p[0] = ('ClassBody', p[1])

#TODO: equivalent_to

def p_subclass_section(p):
    """subclass_section : SUBCLASSOF subclass_expressions"""
    p[0] = ('SubClassOf', p[2])

def p_subclass_expressions(p):
    """subclass_expressions : subclass_expressions SPECIAL subclass_expression
                             | subclass_expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_subclass_expression(p):
    """subclass_expression : PROPERTY SOME IDENTIFIER
                            | PROPERTY ALL IDENTIFIER
                            | PROPERTY VALUE IDENTIFIER
                            | PROPERTY MIN INTEGER
                            | PROPERTY MAX INTEGER
                            | PROPERTY EXACTLY INTEGER
                            | PROPERTY ONLY '(' IDENTIFIER OR IDENTIFIER ')'
                            | PROPERTY SOME TYPE
                            """
    print('parsed a subclass expression', p[1], p[2], p[3])
    p[0] = ('SubClassExpression', p[1], p[2:])

def p_disjoint_section(p):
    """disjoint_section : DISJOINTCLASSES ':' identifier_list"""
    p[0] = ('DisjointClasses', p[3])

def p_identifier_list(p):
    """identifier_list : identifier_list ',' IDENTIFIER
                        | IDENTIFIER"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_individuals_section(p):
    """individuals_section : INDIVIDUALS ':' individual_list"""
    p[0] = ('Individuals', p[3])

def p_individual_list(p):
    """individual_list : individual_list ',' INDIVIDUAL
                        | INDIVIDUAL"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_error(p):
    print("Erro de sintaxe em '%s'" % p.value if p else "EOF")


# Construtor do parser
parser = yacc.yacc()

dataTeste = '''Class: Pizza
 SubClassOf:
 hasBase some PizzaBase,
 hasCaloricContent some xsd:integer
 DisjointClasses:
 Pizza, PizzaBase, PizzaTopping
 Individuals:
 CustomPizza1,
 CustomPizza2
'''

lexer.input(dataTeste)

parser.parse(lexer=lexer)