class Plataforma:
    """
    Classe que recebe uma plataforma onde o conteúdo é consumido ou a interação ocorre
    """
    def __init__(self, nome_plataforma: str):
        """
        Inicializa a plataforma com nome e lista de interações.
        """
        # Valida se o nome da plataforma não está vazio ou apenas com espaços em branco
        if not nome_plataforma or not nome_plataforma.strip():
            raise ValueError("O nome da plataforma não pode estar vazio.")
        
        self.__interacoes = []  # Lista privada de interações na plataforma
        # Usando os setters para definir os atributos
        self.nome_plataforma = nome_plataforma

    @property
    def nome_plataforma(self):
        """Retorna o nome da plataforma."""
        return self.__nome_plataforma

    @nome_plataforma.setter
    def nome_plataforma(self, valor):
        # Validação se o nome não está vazio também no setter, caso haja alterações futuras
        if not valor or not valor.strip():
            raise ValueError("O nome da plataforma não pode ser vazio.")
        self.__nome_plataforma = valor.strip()
        
    @property
    def interacoes(self):
        """Retorna uma cópia da lista de interações para garantir encapsulamento."""
        return list(self.__interacoes)

    def adicionar_interacao(self, interacao):
        """Adiciona uma interação à lista da plataforma."""
        self.__interacoes.append(interacao)
    
    def calcular_tempo_total_consumo(self):
        """
        Retorna o tempo total assistido na plataforma (em segundos).
        """
        return sum(interacao.watch_duration_seconds for interacao in self.__interacoes if hasattr(interacao, 'watch_duration_seconds')) 

    def calcular_total_interacoes_engajamento(self):
        """
        Retorna o total de interações de engajamento ('like', 'share', 'comment') na plataforma.
        """
        return sum(
            1 for interacao in self.__interacoes
            if hasattr(interacao, 'tipo_interacao') and interacao.tipo_interacao in ('like', 'share', 'comment')
        )
    
    def calcular_media_tempo_consumo(self):
        """
        Calcula a média de tempo de consumo por interação com que tenha havido consumo.
        Retorna 0 se não houver interações com tempo de consumo.
        """
        tempos = [
            interacao.watch_duration_seconds
            for interacao in self.__interacoes
            if hasattr(interacao, 'watch_duration_seconds') and interacao.watch_duration_seconds is not None
        ]
        return sum(tempos) / len(tempos) if tempos else 0
    
    def __str__(self):
        # Retorna o nome da plataforma como string
        return self.__nome_plataforma

    def __repr__(self):
        # Retorna uma representação da plataforma no formato Plataforma(nome='...')
        return f"Plataforma(nome='{self.__nome_plataforma}')"

    def __eq__(self, outro):
        # Compara dois objetos Plataforma para igualdade
        if isinstance(outro, Plataforma):
            return self.__nome_plataforma == outro.__nome_plataforma
        return False

    def __hash__(self):
        # Retorna o hash do objeto Plataforma, permitindo seu uso em coleções que dependem de hashing
        return hash((self.__nome_plataforma))