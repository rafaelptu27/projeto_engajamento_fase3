class No:
    def __init__(self, chave, valor):
        self.chave = chave      # Pode ser id_conteudo, id_usuario, etc.
        self.valor = valor      # Pode ser um objeto Conteudo, Usuario, etc.
        self.esquerda = None
        self.direita = None

class ArvoreBinariaBusca:
    def __init__(self):
        self.raiz = None

    def inserir(self, chave, valor):
        """Insere um novo elemento na árvore.
        Complexidade: O(h), h = altura da árvore."""
        if self.raiz is None:
            self.raiz = No(chave, valor)
        else:
            self._inserir(self.raiz, chave, valor)

    def _inserir(self, no_atual, chave, valor):
        if chave < no_atual.chave:
            if no_atual.esquerda is None:
                no_atual.esquerda = No(chave, valor)
            else:
                self._inserir(no_atual.esquerda, chave, valor)
        elif chave > no_atual.chave:
            if no_atual.direita is None:
                no_atual.direita = No(chave, valor)
            else:
                self._inserir(no_atual.direita, chave, valor)
        else:
            no_atual.valor = valor  # Atualiza se já existir

    def buscar(self, chave):
        """Busca um elemento pela chave.
        Complexidade: O(h)."""
        return self._buscar(self.raiz, chave)

    def _buscar(self, no_atual, chave):
        if no_atual is None:
            return None
        if chave == no_atual.chave:
            return no_atual.valor
        elif chave < no_atual.chave:
            return self._buscar(no_atual.esquerda, chave)
        else:
            return self._buscar(no_atual.direita, chave)

    def percurso_em_ordem(self):
        """Retorna uma lista dos valores em ordem de chave.
        Complexidade: O(n)."""
        resultado = []
        self._percurso_em_ordem(self.raiz, resultado)
        return resultado

    def _percurso_em_ordem(self, no_atual, resultado):
        if no_atual:
            self._percurso_em_ordem(no_atual.esquerda, resultado)
            resultado.append(no_atual.valor)
            self._percurso_em_ordem(no_atual.direita, resultado)

    def remover(self, chave):
        """Remove um elemento pela chave.
        Complexidade: O(h)."""
        self.raiz = self._remover(self.raiz, chave)

    def _remover(self, no_atual, chave):
        if no_atual is None:
            return no_atual
        if chave < no_atual.chave:
            no_atual.esquerda = self._remover(no_atual.esquerda, chave)
        elif chave > no_atual.chave:
            no_atual.direita = self._remover(no_atual.direita, chave)
        else:
            if no_atual.esquerda is None:
                return no_atual.direita
            elif no_atual.direita is None:
                return no_atual.esquerda
            temp = self._minimo(no_atual.direita)
            no_atual.chave = temp.chave
            no_atual.valor = temp.valor
            no_atual.direita = self._remover(no_atual.direita, temp.chave)
        return no_atual

    def _minimo(self, no_atual):
        while no_atual.esquerda is not None:
            no_atual = no_atual.esquerda
        return no_atual