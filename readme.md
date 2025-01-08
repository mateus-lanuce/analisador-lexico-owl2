# Projeto de Compiladores

## como rodar o projeto?
1. necessário ter o python instalado com a versão 3.8 ou superior
2. opcionalmente, criar um ambiente virtual com o comando `python -m venv venv` e ativá-lo com o comando `source venv/bin/activate`
3. instalar o pacote `ply` com o comando `pip install ply` ou `pip install -r requirements.txt`
4. rodar o arquivo `owl2lex.py` com o comando `python owl2lex.py`

## Especificações do Analisador Léxico para OWL2 (Manchester Syntax)

### Palavras Reservadas
- SOME, ALL, VALUE, MIN, MAX, EXACTLY, THAT
- NOT
- AND
- OR
- Class, EquivalentTo, Individuals, SubClassOf, DisjointClasses (todos sucedidos por “:”, indicando tipos na linguagem OWL)

### Identificadores de Classes
- Nomes começando com letra maiúscula, por exemplo: `Pizza`
- Nomes compostos concatenados com iniciais maiúsculas, por exemplo: `VegetarianPizza`
- Nomes compostos separados por underline, por exemplo: `Margherita_Pizza`

### Identificadores de Propriedades
- Começando com “has”, seguidos de uma string simples ou composta, por exemplo: `hasSpiciness`, `hasTopping`, `hasBase`
- Começando com “is”, seguidos de qualquer coisa, e terminados com “Of”, por exemplo: `isBaseOf`, `isToppingOf`
- Nomes de propriedades geralmente começam com letra minúscula e são seguidos por qualquer outra sequência de letras, por exemplo: `ssn`, `hasPhone`, `numberOfPizzasPurchased`

### Símbolos Especiais
- Exemplos: `[`, `]`, `{`, `}`, `(`, `)`, `>`, `<`, `,`

### Nomes de Indivíduos
- Começando com uma letra maiúscula, seguida de qualquer combinação de letras minúsculas e terminando com um número, por exemplo: `Customer1`, `Waiter2`, `AmericanHotPizza1`

### Tipos de Dados
- Identificação de tipos nativos das linguagens OWL, RDF, RDFs ou XML Schema, por exemplo: `owl:real`, `rdfs:domain`, `xsd:string`

### Cardinalidades
- Representadas por números inteiros, por exemplo: `hasTopping min 3`

### Como funciona a tabela de simbolos?
- A tabela de simbolos funciona como uma arvore 
- Cada nó da arvore guarda dados como os sibolos daquele nó, o escopo dele e também os filhos deles, ou seja, os escopos filhos.

