from datetime import datetime

class Interacao:
    """
    Classe das Interações dos usuários com os conteúdo.
    """
    TIPOS_INTERACAO_VALIDOS = {'view_start', 'like', 'share', 'comment'} # conjunto com os tipos válidos de interação (atributos de classe)
    
    # Atributo de classe para controle de IDs únicos
    __ids_usados = set()  # Armazena IDs de interações já criados para evitar duplicações
    __proximo_id = 1      # ID a ser atribuído a próxima interação que for criada

    def __init__(self, dados_brutos: dict, conteudo_associado, plataforma_interacao):
        """Construtor recebe:
        Inicializa uma interação a partir dos dados brutos do CSV, do conteúdo e da plataforma.
        """

        while Interacao.__proximo_id in Interacao.__ids_usados:  # Verifica IDs usados
            Interacao.__proximo_id += 1  # Incrementa para encontrar um ID 'livre'
        self.__interacao_id = Interacao.__proximo_id  # Atribui o novo ID à instância
        Interacao.__ids_usados.add(self.__interacao_id)  # Adiciona o ID ao conjunto de IDs usados

        self.__conteudo_associado = conteudo_associado # inicializa o atributo do conteúdo associado

        try:
            self.__id_usuario = int(dados_brutos['id_usuario'])  # Converte o ID do usuário para int
        except (KeyError, ValueError, TypeError):  # Captura exceções relevantes
            raise ValueError("id_usuario inválido ou ausente na interação.") 

        try:
            valor_timestamp = dados_brutos['timestamp_interacao']  # Obtém o timestamp
            self.__timestamp_interacao = datetime.fromisoformat(valor_timestamp) # Converte para datetime
        except Exception:  # Captura qualquer erro na conversão
            raise ValueError("timestamp_interacao inválido ou ausente na interação.")  # Erro se inválido

        self.__plataforma_interacao = plataforma_interacao # inicializa o atributo plataforma da interação
        
        tipo = dados_brutos.get('tipo_interacao', '').strip()  # Obtém o tipo de interação e limpa espaços
        if not tipo: # valida se o tipo foi preenchido
            raise ValueError(f"Tipo de interação não preenchido")  
        if tipo not in Interacao.TIPOS_INTERACAO_VALIDOS: # valida contra os tipos permitidos
            raise ValueError(f"Tipo de interação inválido: {tipo}")  # Erro se tipo inválido
        self.__tipo_interacao = tipo

        valor_duracao = dados_brutos.get('watch_duration_seconds', 0)  # Obtém o tempo assistido ou define como 0
        try:
            duracao = int(valor_duracao)  # Converte para inteiro
            self.__watch_duration_seconds = max(0, duracao)  # Garante que seja não negativo
        except (ValueError, TypeError):  # exceções de conversão
            self.__watch_duration_seconds = 0  # Define como 0 se houver erro

        comentario = dados_brutos.get('comment_text', '')  # Obtém o texto do comentário, define padrão vazio caso não exista
        self.__comment_text = comentario.strip() if comentario else ""  # Limpa espaços ou define como vazio

    # Propriedades (getters) para acesso seguro aos atributos
    @property
    def interacao_id(self):
        """retorna o ID único da interação"""
        return self.__interacao_id

    @property
    def conteudo_associado(self):
       """retorna o Conteudo associado da interação"""
       return self.__conteudo_associado

    @property
    def id_usuario(self):
        """retorna o ID do usuário da interação"""
        return self.__id_usuario

    @property
    def timestamp_interacao(self):
        """retorna Data/hora da interação"""
        return self.__timestamp_interacao

    @property
    def plataforma_interacao(self):
        """retorna a Plataforma da interação"""
        return self.__plataforma_interacao

    @property
    def tipo_interacao(self):
        """retorna o tipo da interação"""
        return self.__tipo_interacao

    @property
    def watch_duration_seconds(self):
        """retorna o tempo de consumo da interação"""
        return self.__watch_duration_seconds

    @property
    def comment_text(self):
        """retorna o comentário da interação"""
        return self.__comment_text

    def __str__(self):
        #Representação amigável da interação
        return (f"Interacao(id={self.__interacao_id}, tipo={self.__tipo_interacao}, "
                f"usuario={self.__id_usuario}, conteudo={self.__conteudo_associado.nome_conteudo})")

    def __repr__(self):
        # Representação detalhada da interação
        return (f"Interacao(id={self.__interacao_id}, tipo='{self.__tipo_interacao}', "
                f"usuario={self.__id_usuario}, conteudo={self.__conteudo_associado}, "
                f"plataforma={self.__plataforma_interacao})")