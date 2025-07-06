from abc import ABC, abstractmethod # Importação do módulo abc para criar classes abstratas

class Conteudo(ABC): # O ABC indica que a classe é abstrata e não pode ser instanciada diretamente
    """
    Classe base abstrata para conteúdos (vídeo, podcast, artigo).
    """
    def __init__(self, id_conteudo: int, nome_conteudo: str, duracao_total: int = None):
        """
        Inicializa o conteúdo com identificador único e nome.
        """
        if not isinstance(id_conteudo, int) or id_conteudo < 0: # Verifica se id_conteudo é um inteiro não negativo
            raise ValueError("O id do conteúdo deve ser um inteiro não negativo.")

        if not nome_conteudo or not nome_conteudo.strip(): # Verifica se nome_conteudo não é vazio ou apenas espaços em branco
            raise ValueError("O nome do conteúdo não pode ser vazio.")
        
        if duracao_total is not None and (not isinstance(duracao_total, int) or duracao_total <0):
            raise ValueError("A duração total deve ser um inteiro não negativo.")
        

        # Inicializa os atributos da classe de forma privada
        self.__id_conteudo = id_conteudo
        self.__nome_conteudo = nome_conteudo.strip()
        self.__duracao_total = duracao_total

        self._interacoes = []  # Inicializa a lista de interações como vazia e protegida (acessível por subclasses)

    @property
    def id_conteudo(self):
        """property que retorna o id do conteúdo"""
        return self.__id_conteudo

    @property
    def nome_conteudo(self):
        """Retorna o nome do conteúdo"""
        return self.__nome_conteudo
    
    @property
    def duracao_total(self):
        """Retorna a duração total do conteúdo em segundos"""
        return self.__duracao_total

    @property
    def interacoes(self):
        """Retorna a lista de interações"""
        return list(self._interacoes)

    def adicionar_interacao(self, interacao):
        """Adiciona uma nova interação à lista de interações"""
        self._interacoes.append(interacao)

    def calcular_total_interacoes_engajamento(self):
        """Calcula o total de interações de engajamento ('like', 'share', 'comment')."""
        # soma 1 para cada interação que seja de um dos tipos de 'engajamento'
        return sum(
            1 for i in self._interacoes
            if hasattr(i, 'tipo_interacao') and i.tipo_interacao in ('like', 'share', 'comment')
        )

    def calcular_contagem_por_tipo_interacao(self):
        """Retorna um dicionário com a contagem de cada tipo de interação."""
        contagem = {}
        # Conta as interações por tipo
        for i in self._interacoes:
            tipo = getattr(i, 'tipo_interacao', None) #busca o tipo da interação em cada objeto de 'interações', definir como None caso não exista evita AttributeError
            if tipo:
                contagem[tipo] = contagem.get(tipo, 0) + 1
        return contagem

    def calcular_tempo_total_consumo(self):
        """Soma o watch_duration_seconds das interações."""
        return sum(i.watch_duration_seconds for i in self._interacoes if hasattr(i, 'watch_duration_seconds'))

    def calcular_media_tempo_consumo(self):
        """Calcula a média de tempo de consumo por interação com que tenha havido consumo."""
        tempos = [
            i.watch_duration_seconds
            for i in self._interacoes
            if hasattr(i, 'watch_duration_seconds') and i.watch_duration_seconds is not None
        ]
        return sum(tempos) / len(tempos) if tempos else 0

    def listar_comentarios(self):
        """Retorna uma lista de comentários presentes nas interações."""
        return [
            i.comment_text
            for i in self._interacoes
            if hasattr(i, 'tipo_interacao') and i.tipo_interacao == 'comment' and i.comment_text
        ]

    @abstractmethod
    def calcular_metricas(self):
        """Método abstrato para ser implementado nas subclasses."""
        pass

    def __str__(self):
        # Representação amigável do conteúdo
        return f"{self.__nome_conteudo} (ID: {self.__id_conteudo}) "

    def __repr__(self):
        # Representação detalhada
        return f"Conteudo(id={self.__id_conteudo}, nome='{self.__nome_conteudo}')"

class Video(Conteudo):
    """
    Classe que representa um vídeo, estendendo a classe Conteudo.
    """
    def __init__(self, id_conteudo: int, nome_conteudo: str, duracao_total: int = None):
        if not isinstance(duracao_total, int) or duracao_total < 0:
            raise ValueError("A duração total do vídeo deve ser um inteiro não negativo.")
        super().__init__(id_conteudo, nome_conteudo, duracao_total)# Inicializa a classe base (Conteudo)
        
    def calcular_metricas(self):
        """
        Sobscreve o método abstrato herdado de "Conteudo"
        Calcula (utilizando as funções herdadas da classe Conteúdo e suas próprias) e retorna as métricas do vídeo
        """
        return {
            "total_interacoes_engajamento": self.calcular_total_interacoes_engajamento(),
            "contagem_por_tipo_interacao": self.calcular_contagem_por_tipo_interacao(),
            "tempo_total_consumo": self.calcular_tempo_total_consumo(),
            "media_tempo_consumo": self.calcular_media_tempo_consumo(),
            "percentual_medio_assistido": self.calcular_percentual_medio_assistido()
        }

    def calcular_percentual_medio_assistido(self):
        """Calcula o percentual médio assistido do vídeo."""
        media_consumo = self.calcular_media_tempo_consumo()
                
        if not self.duracao_total:
            return "Não há informação da duração total do conteúdo"
        if self.duracao_total > 0:
            return round((media_consumo / self.duracao_total) * 100, 2)
        return 0.0

class Podcast(Conteudo):
    """
    Classe que representa um podcast, estendendo a classe Conteudo.
    """
    def __init__(self, id_conteudo: int, nome_conteudo: str, duracao_total: int =None):
        if duracao_total is not None and (not isinstance(duracao_total, int) or duracao_total < 0):
            raise ValueError("A duração total do episódio deve ser um inteiro não negativo.")
        super().__init__(id_conteudo, nome_conteudo, duracao_total)
        
    def calcular_metricas(self):
        """
        Sobscreve o método abstrato herdado de "Conteudo"
        Calcula (utilizando as funções herdadas da classe Conteúdo e suas próprias) e retorna as métricas do Podcast
        """
        return {
            "total_interacoes_engajamento": self.calcular_total_interacoes_engajamento(),
            "contagem_por_tipo_interacao": self.calcular_contagem_por_tipo_interacao(),
            "tempo_total_consumo": self.calcular_tempo_total_consumo(),
            "media_tempo_consumo": self.calcular_media_tempo_consumo(),
            "percentual_medio_ouvido": self._calcular_percentual_medio_ouvido()
        }

    def _calcular_percentual_medio_ouvido(self):
        """
        Calcula o percentual médio ouvido do podcast.
        """
        media_consumo = self.calcular_media_tempo_consumo()
        
        if not self.duracao_total:
            return "Não há informação da duração total do conteúdo"
        if self.duracao_total > 0:
            return round((media_consumo / self.duracao_total) * 100, 2)
        return 0.0

class Artigo(Conteudo):
    """
    Classe que representa um artigo, estendendo a classe Conteudo.
    """
    def __init__(self, id_conteudo, nome_conteudo, tempo_leitura_estimado_segundos=None):
        if tempo_leitura_estimado_segundos is not None and (not isinstance(tempo_leitura_estimado_segundos, int) or tempo_leitura_estimado_segundos < 0):
            raise ValueError("O tempo de leitura estimado deve ser um inteiro não negativo.")
        super().__init__(id_conteudo, nome_conteudo, tempo_leitura_estimado_segundos)



    def calcular_metricas(self):
        """
        Calcula e retorna todas as métricas relevantes para o artigo.
        """
        return {
            "total_interacoes_engajamento": self.calcular_total_interacoes_engajamento(),
            "contagem_por_tipo_interacao": self.calcular_contagem_por_tipo_interacao(),
            "tempo_total_consumo": self.calcular_tempo_total_consumo(),
            "media_tempo_consumo": self.calcular_media_tempo_consumo(),
            "percentual_medio_lido": self._calcular_percentual_medio_lido()
        }

    def _calcular_percentual_medio_lido(self):
        """
        Calcula o percentual médio lido do artigo.
        """
        media_consumo = self.calcular_media_tempo_consumo()
        if not self.duracao_total:
            return "Não há informação da duração total do conteúdo"
        if self.duracao_total > 0:
            return round((media_consumo / self.duracao_total) * 100, 2)
        return 0.0