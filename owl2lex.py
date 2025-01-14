#------------------------------------
# owl2lex.py
# Especificar um analisador léxico para a linguagem OWL2 no formato Manchester Syntax, considerando as seguintes especificações:
# Palavras reservadas:
# ● SOME, ALL, VALUE, MIN, MAX, EXACTLY, THAT
# ● NOT
# ● AND
# ● OR
# ● Class, EquivalentTo, Individuals, SubClassOf, DisjointClasses (todos sucedidos por “:”, que indicam tipos na linguagem OWL)
# 
# Identificadores de classes:
# ● Nomes começando com letra maiúscula, p.ex.: Pizza.
# ● Nomes compostos concatenados e com iniciais maiúsculas, p.ex.: VegetarianPizza.
# ● Nomes compostos separados por underline, p.ex.: Margherita_Pizza.
# 
# Identificadores de propriedades:
# ● Começando com “has”, seguidos de uma string simples ou composta, p.ex.: hasSpiciness, hasTopping, hasBase.
# ● Começando com “is”, seguidos de qualquer coisa, e terminados com “Of”, p.ex.: isBaseOf, isToppingOf.
# ● Nomes de propriedades geralmente começam com letra minúscula e são seguidos por qualquer outra sequência de letras, p.ex: ssn, hasPhone, numberOfPizzasPurchased.
# 
# Símbolos especiais:
# ● Exemplos: [, ], {, }, (, ), >, <, e “,”
# 
# Nomes de indivíduos:
# ● Começando com uma letra maiúscula, seguida de qualquer combinação de letras minúsculas e
# terminando com um número. Por exemplo: Customer1, Waiter2, AmericanHotPizza1, etc.
# 
# Tipos de dados:
# ● Identificação de tipos nativos das linguagens OWL, RDF, RDFs ou XML Schema, por exemplo: owl:
# real, rdfs: domain, ou xsd: string.
# 
# Cardinalidades:
# ● Representadas por números inteiros, p.ex.: hasTopping min 3
#------------------------------------

import ply.lex as lex
from SymbolTable import SymbolTableTree

reserved = {
    'SOME': 'SOME',
    'ONLY': 'ONLY',
    'ALL': 'ALL',
    'VALUE': 'VALUE',
    'MIN': 'MIN',
    'MAX': 'MAX',
    'EXACTLY': 'EXACTLY',
    'THAT': 'THAT',
    'NOT': 'NOT',
    'AND': 'AND',
    'OR': 'OR',
    'Class:': 'CLASS',
    'EquivalentTo:': 'EQUIVALENTO',
    'Individuals:': 'INDIVIDUALS',
    'SubClassOf:': 'SUBCLASSOF',
    'DisjointClasses:': 'DISJOINTCLASSES'
}

tokens = [
    'IDENTIFIER',
    'INDIVIDUAL',
    'PROPERTY',
    'INTEGER',
    'SPECIAL',
    'TYPE'
] + list(reserved.values())

#ignorar espaços e tabs
t_ignore = ' \t'

# Criando a tabela de símbolos com escopos
symbol_table = SymbolTableTree()

#ignorar comentários
def t_COMMENT(t):
    r'\#.*'
    pass

#contar quebra de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#A ordem das funcoes de tokens é importante

#identificar inteiros
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)

    # Adicionar à tabela de símbolos com o tipo e o valor
    symbol_table.add_symbol(t.value, t.type)
    return t

#identificar símbolos especiais
def t_SPECIAL(t):
    r'\[|\]|\{|\}|\(|\)|>|<|,'
    symbol_table.add_symbol(t.value, t.type)
    return t

#identificar tipos de dados
def t_TYPE(t):
    r'owl:real|rdfs:domain|xsd:string|xsd:integer'
    symbol_table.add_symbol(t.value, t.type)
    return t

#identificar individuos
def t_INDIVIDUAL(t):
    r'[A-Z][A-Za-z]+[0-9]+'
    symbol_table.add_symbol(t.value, t.type)
    return t

#identificar propriedades
def t_PROPERTY(t):
    r'(has[a-zA-Z0-9_]+)|(is.+Of)|([a-z][a-zA-Z]+)'
    #verificar se é uma palavra reservada até a 10ª ignorando maiúsculas e minúsculas
    if t.value.upper() in reserved:
        t.type = reserved[t.value.upper()]
        symbol_table.add_symbol(t.value, t.type)
    else:
        t.type = 'PROPERTY'
        # Adicionar à tabela de símbolos como propriedade
        symbol_table.add_symbol(t.value, t.type)
    return t

#IMPORTANTE VIR DEPOIS - identificar identificadores
def t_IDENTIFIER(t):
    r'([A-Z][a-zA-Z]+:)|([A-Z][a-z]+_[A-Z][a-z]+)|([A-Z][a-z]+([A-Z][a-z]+)?)|([a-z]+)'

    #verificar se é uma palavra reservada até a 10ª ignorando maiúsculas e minúsculas
    if t.value.upper() in reserved:
        t.type = reserved[t.value.upper()]
        symbol_table.add_symbol(t.value, t.type)
    else:
        t.type = reserved.get(t.value, 'IDENTIFIER')   #se não for, é um identificador ou classe)

        # nesse momento deve-se verificar o escopo da tabela de símbolos
        # se for uma classe, deve adicionar o identificador à tabela de símbolos e criar um novo escopo
        if t.type == 'CLASS':
            #verificar se é o escopo global
            if symbol_table.is_global_scope():
                symbol_table.add_symbol(t.value, t.type)
                symbol_table.enter_scope(t.type)
            else:
                #ir para o escopo global e adicionar o identificador, pois classes são globais
                symbol_table.go_to_global_scope()
                symbol_table.add_symbol(t.value, t.type)
                symbol_table.enter_scope(t.type)
        elif t.type == 'EQUIVALENTO' or t.type == 'INDIVIDUALS' or t.type == 'SUBCLASSOF' or t.type == 'DISJOINTCLASSES':
            #sair do escopo atual se não for o escopo de classe
            if symbol_table.get_current_scope() != 'CLASS':
                symbol_table.exit_scope()
            symbol_table.add_symbol(t.value, t.type)
            symbol_table.enter_scope(t.type)
        else:
            symbol_table.add_symbol(t.value, t.type)
        
    return t

#identificar erros
def t_error(t):
    print("Caractere ilegal: ", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()


# Teste
data = '''
Class: Customer
    EquivalentTo:
        Person
        and (purchasedPizza some Pizza)
        and (hasPhone some xsd:string)
    Individuals:
        Customer1,
        Customer10,
        Customer2,
        Customer3,
        Customer4,
        Customer5,
        Customer6,
        Customer7,
        Customer8,
        Customer9
Class: Employee
    SubClassOf:
        Person
        and (ssn min 1 xsd:string)
    Individuals:
        Chef1,
        Manager1,
        Waiter1,
        Waiter2
Class: Pizza
    SubClassOf:
        hasBase some PizzaBase,
        hasCaloricContent some xsd:integer
    DisjointClasses:
        Pizza, PizzaBase, PizzaTopping
    Individuals:
        CustomPizza1,
        CustomPizza2
Class: CheesyPizza
    EquivalentTo:
        Pizza
        and (hasTopping some CheeseTopping)
    Individuals:
        CheesyPizza1
Class: HighCaloriePizza
    EquivalentTo:
        Pizza
        and (hasCaloricContent some xsd:integer[>= 400])
Class: InterestingPizza
    EquivalentTo:
        Pizza
        and (hasTopping min 3 PizzaTopping)
Class: LowCaloriePizza
    EquivalentTo:
        Pizza
        and (hasCaloricContent some xsd:integer[< 400])
Class: NamedPizza
    SubClassOf:
      Pizza
Class: AmericanaHotPizza
    SubClassOf:
        NamedPizza,
        hasTopping some JalapenoPepperTopping,
        hasTopping some MozzarellaTopping,
        hasTopping some PepperoniTopping,
        hasTopping some TomatoTopping
    DisjointClasses:
        AmericanaHotPizza, AmericanaPizza, MargheritaPizza, SohoPizza
    Individuals:
        AmericanaHotPizza1,
        AmericanaHotPizza2,
        AmericanaHotPizza3,
        ChicagoAmericanaHotPizza1
Class: AmericanaPizza
    SubClassOf:
        NamedPizza,
        hasTopping some MozzarellaTopping,
        hasTopping some PepperoniTopping,
        hasTopping some TomatoTopping
    DisjointClasses:
        AmericanaHotPizza, AmericanaPizza, MargheritaPizza, SohoPizza
    Individuals:
        AmericanaPizza1,
        AmericanaPizza2
Class: MargheritaPizza
    SubClassOf:
        NamedPizza,
        hasTopping some MozzarellaTopping,
        hasTopping some TomatoTopping,
        hasTopping only
        (MozzarellaTopping or TomatoTopping)
    DisjointClasses:
        AmericanaHotPizza, AmericanaPizza, MargheritaPizza, SohoPizza
    Individuals:
        MargheritaPizza1,
        MargheritaPizza2
Class: SohoPizza
    SubClassOf:
        NamedPizza,
        hasTopping some MozzarellaTopping,
        hasTopping some OliveTopping,
        hasTopping some ParmesanTopping,
        hasTopping some TomatoTopping,
        hasTopping only
        (MozzarellaTopping or OliveTopping or ParmesanTopping or TomatoTopping)
    DisjointClasses:
      AmericanaHotPizza, AmericanaPizza, MargheritaPizza, SohoPizza
    Individuals:
        SohoPizza1,
        SohoPizza2
Class: SpicyPizza
    EquivalentTo:
        Pizza
        and (hasTopping some (hasSpiciness value Hot))
Class: VegetarianPizza
    EquivalentTo:
        Pizza
        and (hasTopping only
        (CheeseTopping or VegetableTopping))
Class: PizzaBase
    DisjointClasses:
        Pizza, PizzaBase, PizzaTopping
Class: PizzaTopping
    DisjointClasses:
        Pizza, PizzaBase, PizzaTopping
Class: Spiciness
EquivalentTo:
{Hot , Medium , Mild}
'''

# lexer.input(data)

# while True:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
    
# print('\n Tabela de Símbolos:')
# print(symbol_table.print_tree())

# Resultado esperado:
# ('CLASS', 'Class:')
# ('IDENTIFIER', 'Pizza')
# ('EQUIVALENTO', 'EquivalentTo:')
# ('PROPERTY', 'hasTopping')
# ('SOME', 'some')
# ('IDENTIFIER', 'TomatoTopping')
# ('INDIVIDUALS', 'Individuals:')
# ('INDIVIDUAL', 'AmericanHotPizza1')
# ('SUBCLASSOF', 'SubClassOf:')
# ('IDENTIFIER', 'Pizza')
# ('DISJOINTCLASSES', 'DisjointClasses:')
# ('IDENTIFIER', 'Pizza')

