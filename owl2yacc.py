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
    p[0] = ('ClassDeclaration', p[1], p[2], p[3])

    if p[3][0] == 'ClassBodyPrimitive':
        print('\nclasse primitiva declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyPrimitiveClosure':
        print('\nclasse primitiva com axioma de fechamento declarada: \n', p[1], p[2], p[3])

def p_class_body(p):
    """class_body : primitive_body
                    | defined_body
                  """
    
    if p[1][0] == 'primitiveBody':
        p[0] = ('ClassBodyPrimitive', p[1:])
    elif p[1][0] == 'primitiveBodyClosure':
        p[0] = ('ClassBodyPrimitiveClosure', p[1:])

    #TODO: adicionar regras para defined_body

def p_class_body_error(p):
    """class_body : error"""
    print('Erro de sintaxe na declaração de classe')

def p_primitive_body(p):
    """primitive_body : subclass_section disjoint_section individuals_section
                   | subclass_section disjoint_section
                   | subclass_section individuals_section
                   | subclass_section
                      """

    if p[1][0] == 'SubClassOf':
        p[0] = ('primitiveBody', p[1])
    elif p[1][0] == 'SubClassOfClosure':
        p[0] = ('primitiveBodyClosure', p[1])

#classe definida
def p_defined_body(p):
    """defined_body : equivalent_section disjoint_section individuals_section
                   | equivalent_section disjoint_section
                   | equivalent_section individuals_section
                   | equivalent_section
                      """
    
    if p[1][0] == 'EquivalentExpression':        
      print('classe definida: ', p[1:])
      p[0] = ('ClassBody', p[1])
    elif p[1][0] == 'CoveredClass':
        print('classe coberta: ', p[1:])
        p[0] = ('ClassBodyCovered', p[1])
    elif p[1][0] == 'NumeredClass':
         print('classe numerada: ', p[1:])
         p[0] = ('ClassBodyNumered', p[1])

def p_subclass_section(p):
    """subclass_section : SUBCLASSOF subclass_expressions"""
    # se tiver uma subclassExpressionClosure, modificar para SubClassOfClosure, necessario percorrer a lista de subclass_expressions
    for i in p[2]:
        if i[0] == 'SubClassExpressionClosure':
            p[0] = ('SubClassOfClosure', *p[2:])
            return

    p[0] = ('SubClassOf', *p[2:])

def p_subclass_section_error(p):
    """subclass_section : error"""
    print('Erro de sintaxe na declaração de subclasse')
    
def p_subclass_expressions(p):
    """subclass_expressions : subclass_expressions SPECIAL subclass_expression
                             | subclass_expression
                             """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_subclass_expressions_error(p):
    """subclass_expressions : error"""
    print('Erro de sintaxe na declaração de expressão de subclasse')

def p_subclass_expression(p):
    """subclass_expression : PROPERTY SOME IDENTIFIER
                            | PROPERTY ALL IDENTIFIER
                            | PROPERTY VALUE IDENTIFIER
                            | PROPERTY MIN INTEGER
                            | PROPERTY MAX INTEGER
                            | PROPERTY EXACTLY INTEGER
                            | PROPERTY SOME TYPE
                            | PROPERTY SOME SPECIAL PROPERTY VALUE TYPE SPECIAL
                            | IDENTIFIER
                            | PROPERTY ONLY SPECIAL IDENTIFIER OR IDENTIFIER SPECIAL
                            """
    if len(p) == 2:
        print ('analisado uma subclass_expression de identificador', p[1])
        p[0] = ('SubClassExpression', p[1])
    elif len(p) == 8:
        print('analisado uma subclass_expression com axioma de fechamento', p[1], p[2], p[3], p[4], p[5], p[6])
        p[0] = ('SubClassExpressionClosure', p[1], p[2], p[3], p[4], p[5], p[6])
    else:
        print('analisado uma subclass_expression', p[1], p[2], p[3])
        p[0] = ('SubClassExpression', p[1], p[2:])   

def p_subclass_expression_error(p):
    """subclass_expression : error"""
    print('Erro de sintaxe na declaração de subclasse') 

def p_disjoint_section(p):
    """disjoint_section : DISJOINTCLASSES identifier_list"""
    p[0] = ('DisjointClasses', p[2])

def p_disjoint_section_error(p):
    """disjoint_section : error"""
    print('Erro de sintaxe na declaração de disjoint classes')

def p_identifier_list(p):
    """identifier_list : identifier_list SPECIAL IDENTIFIER
                        | IDENTIFIER"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = list()
        p[0].append(p[1])
        if type(p[1]) == list:
            p[1].append(p[3])
            p[0].append(p[1])
        else:
            p[0].append(p[3])

def p_identifier_list_error(p):
    """identifier_list : error"""
    print('Erro de sintaxe na declaração de lista de identificadores')

def p_individuals_section(p):
    """individuals_section : INDIVIDUALS individual_list"""
    p[0] = ('Individuals', p[2:])

def p_individuals_section_error(p):
    """individuals_section : error"""
    print('Erro de sintaxe na declaração de individuos')

def p_individual_list(p):
    """individual_list : individual_list SPECIAL INDIVIDUAL
                        | INDIVIDUAL"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = list()
        p[0].append(p[1])
        p[0].append(p[3])

def p_individual_list_error(p):
    """individual_list : error"""
    print('Erro de sintaxe na declaração de lista de individuos')
    
def p_equivalent_section(p): 
    """equivalent_section :  EQUIVALENTO equivalent_expressions"""
    for i in p[2]:
        if i[0] == 'EquivalentoCoveredClass':
            p[0] = ('CoveredClass', *p[2:])
            return
        elif i[0] == 'EquivalentoNumeredClass':
            p[0] == ('NumeredClass', *p[2:])
            return
    
    p[0] = ('EquivalentExpression', *p[2:])

def p_equivalent_expressions(p):
    """equivalent_expressions : equivalent_expressions SPECIAL equivalent_expression
                                | equivalent_expression
                                """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_equivalent_expression(p):
    """equivalent_expression : IDENTIFIER AND SPECIAL complex_property_expression SPECIAL
                               | SPECIAL identifier_list SPECIAL
                               | TYPE OR TYPE OR TYPE
                               """
    
    if len(p) == 6 and p[2] == 'and':
        print('Analisando uma expressao de classe definida', *p[1:])
        p[0] = ('EquivalentExpression', *p[1:])

        if p[4][0] == 'ComplexPropertyExpressionAninhada':
            print('Analisando uma expressao de classe aninhada', *p[4])
            p[0] = ('EquivalentExpressionAninhada', *p[1:])
    elif len(p) == 7:
        print('Analisando uma classe numerada')
        p[0] = ('EquivalentoNumeredClass', *p[1:])

def p_complex_property_expression_equivalent_to(p):
    """complex_property_expression : PROPERTY SOME IDENTIFIER
                                      | PROPERTY SOME SPECIAL PROPERTY VALUE IDENTIFIER SPECIAL
                                      """
    if len(p) == 8:
       print('Analisando uma propriedade complexa aninhada', *p[1:])
       p[0] = ('ComplexPropertyExpressionAninhada', *p[1:])
    else:
        print('Analisando uma propriedade complexa', *p[1:])
        p[0] = ('ComplexPropertyExpression', *p[1:])



def p_error(p):
    print("Erro de sintaxe em '%s'" % p.value if p else "EOF")


# Construtor do parser
parser = yacc.yacc()

dataTeste = '''Class: SpicyPizza
EquivalentTo:
Pizza
and (hasTopping some (hasSpiciness value Hot))
'''

lexer.input(dataTeste)

parser.parse(lexer=lexer)