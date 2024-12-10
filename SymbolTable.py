class SymbolTableTree(Exception):
    class ScopeNode:
        def __init__(self, name):
            self.name = name
            self.symbols = {}  # Dicionário de símbolos no escopo
            self.children = []  # Lista de sub-escopos
            self.parent = None  # Escopo pai

    def __init__(self):
        self.global_scope = self.ScopeNode("global")  # Nó raiz da árvore
        self.current_scope = self.global_scope  # Escopo atual

    def enter_scope(self, scope_name):
        """
        Entra em um novo escopo, criando um nó filho no escopo atual.
        """
        new_scope = self.ScopeNode(scope_name)
        new_scope.parent = self.current_scope
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        """
        Sai do escopo atual, voltando ao escopo pai.
        """
        if self.current_scope.parent is None:
            raise Exception("Já no escopo global, não é possível sair.")
        self.current_scope = self.current_scope.parent

    def add_symbol(self, name, symbol_type):
        """
        Adiciona um símbolo ao escopo atual, se ele ainda não existir.
        """
        if not name in self.current_scope.symbols:
            self.current_scope.symbols[name] = {'type': symbol_type}     

    def find_symbol(self, name):
        """
        Procura um símbolo começando pelo escopo atual e subindo na hierarquia.
        """
        scope = self.current_scope
        while scope:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def print_tree(self, node=None, level=0):
        """
        Imprime a árvore de escopos de forma hierárquica.
        """
        if node is None:
            node = self.global_scope
        print("  " * level + f"Scope: {node.name}")
        for symbol, details in node.symbols.items():
            print("  " * (level + 1) + f"Symbol: {symbol}, Type: {details['type']}")
        for child in node.children:
            self.print_tree(child, level + 1)
    
    def is_global_scope(self):
        return self.current_scope == self.global_scope
    
    def get_current_scope(self):
        return self.current_scope.name
    
    def print_current_scope(self):
        print(self.current_scope.name)
    
    def go_to_global_scope(self):
        self.current_scope = self.global_scope


# # Criação da tabela de símbolos
# symbol_table = SymbolTableTree()

# # Adicionando símbolos ao escopo global
# symbol_table.add_symbol("Pizza", "CLASS")
# symbol_table.add_symbol("CheeseTopping", "CLASS")

# # Entrando no escopo de 'Pizza'
# symbol_table.enter_scope("Pizza")
# symbol_table.add_symbol("hasTopping", "PROPERTY")
# symbol_table.add_symbol("caloricContent", "PROPERTY")

# # Entrando no escopo de 'hasTopping'
# symbol_table.enter_scope("hasTopping")
# symbol_table.add_symbol("Spiciness", "ATTRIBUTE")
# symbol_table.exit_scope()

# # Voltando ao escopo de 'Pizza' e saindo para o global
# symbol_table.exit_scope()

# # Imprimindo a árvore de escopos
# symbol_table.print_tree()
