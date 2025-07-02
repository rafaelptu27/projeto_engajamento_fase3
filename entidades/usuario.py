class Usuario:
    """
    Representa um usuário da plataforma, armazenando suas interações.
    """
    def __init__(self, id_usuario: int):
        """
        Inicializa o usuário com identificador único.
        """
        # Validação para garantir que o id seja um inteiro não negativo
        if not isinstance(id_usuario, int) or id_usuario < 0:
            raise ValueError("O id do usuário deve ser um inteiro não negativo.")
        self.__id_usuario = id_usuario
        self.__interacoes = []  # Lista privada de interações do usuário

    @property
    def id_usuario(self):
        """Retorna o ID do usuário."""
        return self.__id_usuario

    @property
    def interacoes(self):
        """Retorna uma cópia da lista de interações para garantir encapsulamento."""
        return list(self.__interacoes)

    def adicionar_interacao(self, interacao):
        """Adiciona uma interação à lista do usuário."""
        self.__interacoes.append(interacao)

    def filtrar_interacoes_por_tipo(self, tipo):
        """Retorna uma lista de interações do usuário de um tipo específico."""
        return [i for i in self.__interacoes if hasattr(i, 'tipo_interacao') and i.tipo_interacao == tipo]

    def obter_conteudos_unicos(self):
        """Retorna um conjunto de conteúdos únicos com os quais o usuário interagiu."""
        return set(i.conteudo_associado for i in self.__interacoes if hasattr(i, 'conteudo_associado'))

    def calcular_tempo_total_em_plataforma(self, plataforma):
        """Soma o tempo de consumo do usuário em uma plataforma específica."""
        return sum(
            i.watch_duration_seconds for i in self.__interacoes
            if hasattr(i, 'plataforma_interacao') and i.plataforma_interacao == plataforma
        )

    def plataformas_mais_frequentes(self, top_n=3):
        """Retorna as plataformas onde o usuário mais interagiu, em ordem decrescente de frequência."""
        from collections import Counter # Importa a classe Counter, que serve para contar elementos em uma coleção
        plataformas = [i.plataforma_interacao for i in self.__interacoes if hasattr(i, 'plataforma_interacao')]

        # usa o counter para contar quantas vezes cada plataforma aparece na lista e .most_common para retornar a lista de mais frequentes
        return Counter(plataformas).most_common(top_n)

    def calcular_tempo_total_assistido(self):
        """
        Retorna o tempo total assistido pelo usuário em todas as plataformas (em segundos).
        """
        plataformas = set(interacao.plataforma_interacao for interacao in self.interacoes)
        total = 0
        for plataforma in plataformas:
            total += self.calcular_tempo_total_em_plataforma(plataforma)
        return total 

    def __str__(self):
        return f"Usuário {self.__id_usuario}"

    def __repr__(self):
        return f"Usuario(id={self.__id_usuario})"