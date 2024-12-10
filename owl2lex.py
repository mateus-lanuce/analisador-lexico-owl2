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

reserved = {
    'SOME': 'SOME',
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


class SymbolTable:
    
    def __init__(self):   
        self.symbols = {}
    
    contador = 0

    def addSymbol(self, name, type, contador=1):
        if name in self.symbols: # se o lexema já existir na tabela de simbolos, incrementa o contador para mostrar quantas vezes o mesmo ocorreu no texto
            contador = contador + 1
        self.symbols[name] = { 
            "type": type,
            "contador": contador,
            #"atributtes": atributtes or {}
        }
    
    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.symbols.items())
            
symbol_table = SymbolTable()

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
    return t

#identificar símbolos especiais
def t_SPECIAL(t):
    r'\[|\]|\{|\}|\(|\)|>|<|,'
    return t

#identificar tipos de dados
def t_TYPE(t):
    r'owl:real|rdfs:domain|xsd:string|xsd:integer'
    return t

#identificar individuos
def t_INDIVIDUAL(t):
    r'[A-Z][A-Za-z]+[0-9]+'
    symbol_table.addSymbol(t.value, 'INDIVIDUAL')
    return t

#identificar propriedades
def t_PROPERTY(t):
    r'(has[a-zA-Z0-9_]+)|(is.+Of)|([a-z][a-zA-Z]+)'
    #verificar se é uma palavra reservada até a 10ª ignorando maiúsculas e minúsculas
    if t.value.upper() in reserved:
        t.type = reserved[t.value.upper()]
    else:
        t.type = 'PROPERTY'
        # Adicionar à tabela de símbolos como propriedade
        symbol_table.addSymbol(t.value, 'PROPERTY')
    return t

#IMPORTANTE VIR DEPOIS - identificar identificadores
def t_IDENTIFIER(t):
    r'([A-Z][a-zA-Z]+:)|([A-Z][a-z]+_[A-Z][a-z]+)|([A-Z][a-z]+([A-Z][a-z]+)?)|([a-z]+)'

    #verificar se é uma palavra reservada até a 10ª ignorando maiúsculas e minúsculas
    if t.value.upper() in reserved:
        t.type = reserved[t.value.upper()]
    else:
        t.type = reserved.get(t.value, 'IDENTIFIER')   #se não for, é um identificador ou classe)
        symbol_table.addSymbol(t.value,'IDENTIFIER')

    #TODO: se for uma classe modificar o escopo da tabela de símbolos, a tabela de simbolos deve verificar se a classe já existe e se não, adicionar
    #e quando o identificar aparecer ver se a classe existe na tabela de símbolos e se não, retornar erro
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

lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
    
print('\n Tabela de Símbolos:')
print(symbol_table)

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

