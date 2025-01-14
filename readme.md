# Projeto de Compiladores: Analisador Léxico e Sintático para OWL2 (Manchester Syntax)

Este projeto implementa um analisador léxico e sintático para uma parte da sintaxe Manchester do OWL2, uma linguagem de ontologia. Ele utiliza as bibliotecas `ply` (Python Lex-Yacc) para análise léxica e sintática.

## Como Executar o Projeto

1.  **Pré-requisitos:** Certifique-se de ter o Python 3.8 ou superior instalado.

2.  **Ambiente Virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv        # Cria um ambiente virtual
    source venv/bin/activate  # Ativa o ambiente (Linux/macOS)
    venv\Scripts\activate     # Ativa o ambiente (Windows)
    ```

3.  **Instalação de Dependências:**
    ```bash
    pip install ply            # Instala o PLY
    # ou
    pip install -r requirements.txt # Instala todas as dependências listadas em requirements.txt
    ```

4.  **Execução:**
    ```bash
    python owl2lex.py      # Executa o analisador léxico
    python owl2yacc.py     # Executa o analisador sintático
    ```

## Analisador Léxico (`owl2lex.py`)

O analisador léxico tokeniza a entrada OWL2 (Manchester Syntax) em unidades léxicas (tokens). Ele reconhece os seguintes elementos:

*   **Palavras Reservadas:** `SOME`, `ALL`, `VALUE`, `MIN`, `MAX`, `EXACTLY`, `THAT`, `NOT`, `AND`, `OR`, `Class`, `EquivalentTo`, `Individuals`, `SubClassOf`, `DisjointClasses`.
*   **Identificadores de Classes:** Nomes começando com letra maiúscula (e.g., `Pizza`, `VegetarianPizza`, `Margherita_Pizza`).
*   **Identificadores de Propriedades:**
    *   Começando com "has" (e.g., `hasSpiciness`, `hasTopping`).
    *   Começando com "is" e terminando com "Of" (e.g., `isBaseOf`, `isToppingOf`).
    *   Outros nomes (e.g., `ssn`, `hasPhone`).
*   **Símbolos Especiais:** `[`, `]`, `{`, `}`, `(`, `)`, `>`, `<`, `,`.
*   **Nomes de Indivíduos:** Começando com letra maiúscula e terminando com um número (e.g., `Customer1`, `AmericanHotPizza1`).
*   **Tipos de Dados:** Tipos nativos de OWL, RDF, RDFS ou XML Schema (e.g., `owl:real`, `rdfs:domain`, `xsd:string`).
*   **Cardinalidades:** Números inteiros (e.g., `hasTopping min 3`).

## Analisador Sintático (`owl2yacc.py`)

O analisador sintático recebe os tokens gerados pelo analisador léxico e verifica se a sequência de tokens segue a gramática definida para a sintaxe Manchester do OWL2. Ele implementa as seguintes regras gramaticais (entre outras):

*   **Declaração de Classe:** `Class: <Identificador> <CorpoDaClasse>`
*   **Corpo da Classe:** Pode ser um corpo primitivo (com subclasses, classes disjuntas e indivíduos), ou um corpo definido (com expressões de equivalência).
*   **Expressões de Subclasse:** Incluem restrições `SOME`, `ALL`, `VALUE`, `MIN`, `MAX`, `EXACTLY` sobre propriedades.
*   **Expressões de Equivalência:** Definem classes como equivalentes a outras expressões de classe, usando `AND`, `OR` e outras construções.
*   **Listas de Identificadores e Indivíduos:** Usadas em declarações de classes disjuntas e indivíduos.

**Estrutura da Árvore Sintática Abstrata (AST):**

O analisador sintático constrói uma Árvore Sintática Abstrata (AST) que representa a estrutura hierárquica do código OWL2 analisado. A AST é representada por tuplas Python, onde o primeiro elemento da tupla é o tipo do nó e os elementos subsequentes são os filhos do nó. Por exemplo, uma declaração de subclasse pode ser representada como:

```python
('SubClassOf', ('SubClassExpression', 'hasTopping', ('SOME', 'CheeseTopping')))
