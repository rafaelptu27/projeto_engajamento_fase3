class Fila:
    def __init__(self):
        self.itens = []

    def enfileirar(self, linha_csv):
        """Adiciona um item ao final da fila. 
        Complexidade: O(1) no caso médio."""
        self.itens.append(linha_csv)

    def desenfileirar(self):
        """Remove e retorna o item do início da fila. 
        Complexidade: O(n) devido ao realocamento da lista."""
        if not self.is_empty():
            return self.itens.pop(0)
        return None

    def is_empty(self):
        """Verifica se a fila está vazia. 
        Complexidade: O(1)."""
        return len(self.itens) == 0

    def tamanho(self):
        """Retorna o tamanho da fila. 
        Complexidade: O(1)."""
        return len(self.itens)