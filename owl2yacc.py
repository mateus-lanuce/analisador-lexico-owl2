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

def showError(error, line, pos = None):
    print('\033[91m' + error + '\033[0m')
    print('\033[91m]' + 'linha: ' + str(line) + '\033[0m')

    if pos:
        print('\033[91m]' + 'posicao: ' + str(pos) + '\033[0m')

# Regras da gramática
def p_class_declaration(p):
    """class_declaration : CLASS IDENTIFIER class_body"""
    p[0] = ('ClassDeclaration', p[1], p[2], p[3])

    if p[3][0] == 'ClassBodyPrimitive':
        print('\nclasse primitiva declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyPrimitiveClosure':
        print('\nclasse primitiva com axioma de fechamento declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyDefined':
        print('\nclasse definida declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyCovered':
        print('\nclasse coberta declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyNumered':
        print('\nclasse numerada declarada: \n', p[1], p[2], p[3])
    elif p[3][0] == 'ClassBodyPrimitiveEnumerated':
        print('\nclasse primitiva enumerada declarada: \n', p[1], p[2], p[3])

def p_class_body(p):
    """class_body : primitive_body
                    | defined_body
                  """
    
    if p[1][0] == 'primitiveBody':
        p[0] = ('ClassBodyPrimitive', p[1:])
    elif p[1][0] == 'primitiveBodyClosure':
        p[0] = ('ClassBodyPrimitiveClosure', p[1:])
    elif p[1][0] == 'primitiveBodyEnumerated':
        p[0] = ('ClassBodyPrimitiveEnumerated', p[1:])
    elif p[1][0] == 'ClassBody':
        p[0] = ('ClassBodyDefined', p[1:])
    elif p[1][0] == 'ClassCovered':
        p[0] = ('ClassBodyCovered', p[1:])
    elif p[1][0] == 'ClassNumered':
        p[0] = ('ClassBodyNumered', p[1:])      
    

    #TODO: adicionar regras para defined_body

def p_class_body_error(p):
    """class_body : error"""
    print('Erro de sintaxe na declaração de classe')

def p_primitive_body(p):
    """primitive_body : subclass_section disjoint_section individuals_section
                   | subclass_section disjoint_section
                   | subclass_section
                      """

    if p[1][0] == 'SubClassOf':
        p[0] = ('primitiveBody', *p[1:])
    elif p[1][0] == 'SubClassOfClosure':
        p[0] = ('primitiveBodyClosure', *p[1:])
    elif p[1][0] == 'SubClassOfEnumerated':
        p[0] = ('primitiveBodyEnumerated', *p[1:])

#classe definida
def p_defined_body(p):
    """defined_body : equivalent_section disjoint_section individuals_section
                   | equivalent_section disjoint_section
                   | equivalent_section
                   | equivalent_section subclass_section disjoint_section individuals_section
                   | equivalent_section subclass_section disjoint_section
                   | equivalent_section subclass_section
                      """
    hasEquivalentExpression = False
    if len(p) > 2:
        if p[1][0] == 'EquivalentExpression':
            hasEquivalentExpression = True
        elif p[2][0] == 'EquivalentExpression':
            hasEquivalentExpression = True
    elif p[1][0] == 'EquivalentExpression':
        hasEquivalentExpression = True

    hasCoveredClass = False
    if len(p) > 2:
        if p[1][0] == 'CoveredClass':
            hasCoveredClass = True
        elif p[2][0] == 'CoveredClass':
            hasCoveredClass = True
    elif p[1][0] == 'CoveredClass':
        hasCoveredClass = True
    
    hasNumeredClass = False
    if len(p) > 2:
        if p[1][0] == 'NumeredClass':
            hasNumeredClass = True
        elif p[2][0] == 'NumeredClass':
            hasNumeredClass = True
    elif p[1][0] == 'NumeredClass':
        hasNumeredClass = True

    switcher = {
        (True, False, False): 'classe definida',
        (False, True, False): 'classe coberta',
        (False, False, True): 'classe numerada'
    }

    switch = switcher[(hasEquivalentExpression, hasCoveredClass, hasNumeredClass)]

    if switch == 'classe definida':
        p[0] = ('ClassBody', *p[1:])
    elif switch == 'classe coberta':
        p[0] = ('ClassCovered', *p[1:])
    elif switch == 'classe numerada':
        p[0] = ('ClassNumered', *p[1:])

def p_subclass_section(p):
    """subclass_section : SUBCLASSOF subclass_expressions"""
    # se tiver uma subclassExpressionClosure, modificar para SubClassOfClosure, necessario percorrer a lista de subclass_expressions
    for i in p[2]:
        if i[0] == 'SubClassExpressionClosure':
            p[0] = ('SubClassOfClosure', *p[2:])
        elif i[0] == 'SubClassExpressionEnumerated':
            p[0] = ('SubClassOfEnumerated', *p[2:])

    #analise da precedencia dos operadores
    if p[0]:
        if p[0][0] == 'SubClassOfClosure':
            try :
                verifyPrecedence(p[0][1])
            except:
                showError('Erro de precedencia na declaração de subclasse', p.lineno(1))

    p[0] = ('SubClassOf', *p[2:])

# Trecho da ontologia de pizzas: neste caso, o axioma de fechamento para
# a propriedade hasTopping (que restringe as imagens da propriedade às classes
# MozzarellaTopping ou TomatoTopping) só pode aparecer depois que as duas triplas
# existenciais (com o operador some) forem declaradas
def verifyPrecedence(p):
    classBeforeOnly = []

    #verificar se a SubClassExpressionClosure é a ultima expressao, disparar erro
    if p[-1][0] == 'SubClassExpression':
        raise Exception()

    for i in p:
        if i[0] == 'SubClassExpression' and len(i) > 2:
            if i[2][0] == 'some':
                classBeforeOnly.append(i[2][1])

    dataInsideOnly = p[-1]

    #verificar se todas as strings de classBeforeOnly estão contidas em dataInsideOnly
    for i in classBeforeOnly:
        if i not in dataInsideOnly:
            raise Exception()

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
                            | PROPERTY ONLY IDENTIFIER
                            | PROPERTY SOME SPECIAL PROPERTY VALUE TYPE SPECIAL
                            | IDENTIFIER
                            | PROPERTY ONLY SPECIAL IDENTIFIER OR IDENTIFIER SPECIAL
                            | SPECIAL identifier_list SPECIAL
                            """
    if len(p) == 2:
            p[0] = ('SubClassExpression', p[1])
    elif len(p) == 8:
        p[0] = ('SubClassExpressionClosure', p[1], p[2], p[3], p[4], p[5], p[6])
    elif len(p) == 4:
        if p[2] == 'identifier_list':
            p[0] = ('SubClassExpressionEnumerated', p[1])
        else:
            p[0] = ('SubClassExpression', p[1], p[2:])
    else:
        p[0] = ('SubClassExpression', p[1], p[2:])   

def p_subclass_expression_error(p):
    """subclass_expression : error"""
    print('Erro de sintaxe na declaração de subclasse') 

def p_disjoint_section(p):
    """disjoint_section : DISJOINTCLASSES identifier_list"""
    p[0] = ('DisjointClasses', p[2])

def p_disjoint_section_error(p):
    """disjoint_section : error"""
    print('Erro de sintaxe na declaração de disjoint classes', p.value)

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
    """equivalent_section : EQUIVALENTO equivalent_expressions"""
    for i in p[2]:
        if i[0] == 'EquivalentoCoveredClass':
            p[0] = ('CoveredClass', *p[2:])
            return
        elif i[0] == 'EquivalentoNumeredClass':
            p[0] = ('NumeredClass', *p[2:])
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
                               | IDENTIFIER OR IDENTIFIER OR IDENTIFIER
                               """
    
    if len(p) == 6 and p[2] == 'and':
        print('Analisando uma expressao de classe definida: ', *p[1:])
        p[0] = ('EquivalentExpression', *p[1:])

        if p[4][0] == 'ComplexPropertyExpressionAninhada':
            print('Analisando uma expressao de classe aninhada: ', *p[4])
            p[0] = ('EquivalentExpressionAninhada', *p[1:])
        
    elif len(p) == 4:
        print('Analisando uma classe numerada: ')
        p[0] = ('EquivalentoNumeredClass', *p[1:])
        
    elif len(p) == 6 and p[2] == 'or':
        print('Analisando uma classe coberta: ')
        p[0] = ('EquivalentoCoveredClass', *p[1:])

def p_complex_property_expression_equivalent_to(p):
    """complex_property_expression : PROPERTY SOME IDENTIFIER
                                      | PROPERTY SOME SPECIAL PROPERTY VALUE IDENTIFIER SPECIAL
                                      | number_complex_expression
                                      """
    if len(p) == 8:
       print('Analisando uma propriedade complexa aninhada', *p[1:])
       p[0] = ('ComplexPropertyExpressionAninhada', *p[1:])
    else:
        print('Analisando uma propriedade complexa', *p[1:])
        p[0] = ('ComplexPropertyExpression', *p[1:])

def p_number_complex_expression(p):
    """number_complex_expression : PROPERTY MIN INTEGER IDENTIFIER
                                    | PROPERTY MAX INTEGER IDENTIFIER
                                    | PROPERTY EXACTLY INTEGER IDENTIFIER
                                    | PROPERTY MIN INTEGER TYPE
                                    | PROPERTY MAX INTEGER TYPE
                                    | PROPERTY EXACTLY INTEGER TYPE
                                    """
    p[0] = p[1:]

def p_number_complex_expression_error(p):
    """number_complex_expression : error"""
    showError('Erro de sintaxe na declaração de expressão de operador numérico', p.lineno, p.lexpos)

def p_equivalent_expression_error(p):
    """equivalent_expression : error"""
    print('Erro de sintaxe na declaração de expressão de equivalência', p.value)

def p_error(p):
    showError('Erro de sintaxe em %s' % p.value if p else 'EOF', p.lineno, p.lexpos)

# Construtor do parser
parser = yacc.yacc()

dataTestePrimitiva = '''
 Class: Pizza
 SubClassOf:
 hasBase some PizzaBase,
 hasCaloricContent some xsd:integer
 DisjointClasses:
 Pizza, PizzaBase, PizzaTopping
 Individuals:
 CustomPizza1,
 CustomPizza2
'''

dataFechamento = '''Class: MargheritaPizza
 SubClassOf:
 NamedPizza,
 hasTopping some MozzarellaTopping,
 hasTopping some TomatoTopping,
 hasTopping only (MozzarellaTopping or TomatoTopping)'''

dataDefinida = '''Class: CheesyPizza
 SubClassOf:
 hasBase some PizzaBase,
 hasCaloricContent some xsd:integer
 EquivalentTo:
 Pizza and (hasTopping some CheeseTopping)
 Individuals:
 CheesyPizza1'''

dataEnumerada = '''Class: Spiciness
 EquivalentTo: {Hot , Medium , Mild}'''

dataCoberta = ''' Class: Spiciness
 EquivalentTo: Hot or Medium or Mild'''

dataErro = '''Class: Pizza
 SubClassOf:
 hasBase some PizzaBase
 DisjointClasses:
 Pizza, PizzaBase PizzaTopping
 Individuals:
 CustomPizza1,
 CustomPizza2
'''

dataPrecedencia1 = '''Class: MargheritaPizza
SubClassOf:
NamedPizza,
hasTopping some MozzarellaTopping,
hasTopping some TomatoTopping,
hasTopping only (MozzarellaTopping or TomatoTopping)
DisjointClasses:
Pizza, PizzaBase, PizzaTopping
Individuals:
MargheritaPizza1,
MargheritaPizza2
'''

dataPrecedenciaErro = '''Class: MargheritaPizza
SubClassOf:
NamedPizza,
hasTopping only (MozzarellaTopping or TomatoTopping),
hasTopping some MozzarellaTopping,
hasTopping some TomatoTopping
DisjointClasses:
Pizza, PizzaBase, PizzaTopping
Individuals:
MargheritaPizza1,
MargheritaPizza2
'''

dataVerifyTipo = '''Class: InterestingPizza
EquivalentTo:
Pizza
and (hasTopping min 3 PizzaTopping)'''

datas = [dataVerifyTipo]

for data in datas:
    print('\n\nAnalisando: \n', data)
    lexer.input(data)
    parser.parse(lexer=lexer)
    print('\n\n')