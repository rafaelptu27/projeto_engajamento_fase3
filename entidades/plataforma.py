class Plataforma:
  """
  Classe que recebe uma plataforma onde o conteúdo é consumido ou a interação ocorre
  """
  def __init__(self, nome_plataforma: str, id_plataforma: int = None):
    """
    Inicializa a plataforma com nome e, opcionalmente, um identificador único.
    """
    # Valida se o nome da plataforma não está vazio ou apenas com espaços em branco
    if not nome_plataforma or not nome_plataforma.strip():
        raise ValueError("O nome da plataforma não pode estar vazio.")

    # Usando os setters para definir os atributos
    self.id_plataforma = id_plataforma
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
    def id_plataforma(self):
        """Retorna o identificador da plataforma"""
        return self.__id_plataforma

    @id_plataforma.setter
    def id_plataforma(self, value):
        # Permite definir o ID explicitamente (usado pelo sistema de orquestração)
        self.__id_plataforma = value

    def __str__(self):
        # Retorna o nome da plataforma como string
        return self.__nome_plataforma

    def __repr__(self):
        # Retorna uma representação da plataforma no formato Plataforma(nome='...')
        return f"Plataforma(nome='{self.__nome_plataforma}')"

    def __eq__(self, outro):
        # Compara dois objetos Plataforma para igualdade
        if isinstance(outro, Plataforma):
            return self.__id_plataforma == outro.__id_plataforma and self.__nome_plataforma == outro.__nome_plataforma
        return False

    def __hash__(self):
        # Retorna o hash do objeto Plataforma, permitindo seu uso em coleções que dependem de hashing
        return hash((self.__id_plataforma, self.__nome_plataforma))