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
                    | defined_body
                    | nested_body
                    | closure_body
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
    p[0] = ('SubClassOf', p[2:])
    
def p_subclass_expressions(p):
    """subclass_expressions : subclass_expressions SPECIAL subclass_expression
                             | subclass_expression
                             | subclass_expressions_only
                             """
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
                            | PROPERTY SOME TYPE
                            | PROPERTY SOME '(' PROPERTY VALUE TYPE ')'
                            | identifier_list
                            | PROPERTY ONLY SPECIAL IDENTIFIER OR IDENTIFIER SPECIAL
                            """
    if len(p) == 2:
        print ('analisado uma subclass_expression', p[1])
        p[0] = ('SubClassExpression', p[1])
    else:
        print('parsed a subclass expression', p[1], p[2], p[3])
        p[0] = ('SubClassExpression', p[1], p[2:])    
    
def p_subclass_section_only(p):
    """subclass_section_only : SUBCLASSOF subclass_expressions_only"""
    p[0] = ('SubClassOf', p[2])

def p_subclass_expressions_only(p):
    """subclass_expressions_only : subclass_expressions_only SPECIAL subclass_expression_only
                             | subclass_expression_only"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_subclass_expression_only(p):
    """subclass_expression_only : PROPERTY ONLY SPECIAL IDENTIFIER OR IDENTIFIER SPECIAL"""
    print('parsed a subclass expression only', p[1], p[2], p[3])
    p[0] = ('SubClassExpression', p[1], p[2:])

def p_disjoint_section(p):
    """disjoint_section : DISJOINTCLASSES identifier_list"""
    p[0] = ('DisjointClasses', p[3])

def p_identifier_list(p):
    """identifier_list : identifier_list ',' IDENTIFIER
                        | IDENTIFIER"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_individuals_section(p):
    """individuals_section : INDIVIDUALS individual_list"""
    p[0] = ('Individuals', p[3])

def p_individual_list(p):
    """individual_list : individual_list ',' INDIVIDUAL
                        | INDIVIDUAL"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
    
def p_equivalent_section(p): 
    """equivalent_section :  EQUIVALENTO identifier_list AND subclass_expression """
    p[0] = p[1] + p[3]

def p_equivalent_section_nested(p):
    """equivalent_section_nested : equivalent_section AND subclass_expression
                                  | equivalent_section AND identifier_list SOME subclass_expression"""
    p[0] = p[1] + p[3]

#na equivalent pode ter, identificador, lista de subclassExpressions

def p_error(p):
    print("Erro de sintaxe em '%s'" % p.value if p else "EOF")


# Construtor do parser
parser = yacc.yacc()

dataTeste = '''Class: MargheritaPizza
SubClassOf:
NamedPizza,
hasTopping some MozzarellaTopping,
hasTopping some TomatoTopping,
hasTopping only (MozzarellaTopping or TomatoTopping)
'''

lexer.input(dataTeste)

parser.parse(lexer=lexer)