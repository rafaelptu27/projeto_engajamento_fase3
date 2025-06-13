"""
Módulo sistema.py
Classe principal de orquestração do Projeto

Responsável por:
- Gerenciar entidades: Plataforma, Conteudo, Usuario
- Controlar geração de IDs únicos para plataformas, respeitando IDs do CSV
- Carregar e processar dados do CSV de interações
- Gerar relatórios de análise
"""

import csv
from entidades.plataforma import Plataforma
from entidades.conteudo import Video, Podcast, Artigo
from entidades.interacao import Interacao
from entidades.usuario import Usuario
from datetime import timedelta


class SistemaAnaliseEngajamento:
    """
    Classe de orquestração do sistema de análise de engajamento.
    Gerencia plataformas, conteúdos, usuários e processa interações.
    """
    VERSAO_ANALISE = "2.0"

    def __init__(self):
        # Dicionários privados conforme especificação
        self.__plataformas_registradas = {}    # plataforma (str) -> Plataforma
        self.__conteudos_registrados = {}      # id_conteudo (int) -> Conteudo
        self.__usuarios_registrados = {}       # id_usuario (int) -> Usuario
        self.__ids_plataformas_existentes = set() # Conjunto para armazenar IDs já usados (do CSV e gerados)

    def _encontrar_id_disponivel(self):
        """
        Encontra o menor ID de plataforma não utilizado, mesmo que haja lacunas.
        """
        id_candidato = 1
        while id_candidato in self.__ids_plataformas_existentes:
            id_candidato += 1
        return id_candidato

    # Métodos de gerenciamento de plataforma
    def cadastrar_plataforma(self, nome_plataforma: str, id_plataforma: int = None):
        """
        Cadastra uma nova plataforma se não existir. Retorna o objeto Plataforma.
        Se o ID for fornecido (do CSV), atualiza o controle para evitar duplicação.
        Se não, gera um ID único internamente, preenchendo lacunas.
        """
        nome = nome_plataforma.strip().lower()
        if not nome:
            raise ValueError("O nome da plataforma não pode estar vazio.")
        if nome in self.__plataformas_registradas: # Se já existe por nome, retorna a plataforma já registrada
            return self.__plataformas_registradas[nome]
        
        # Se id informado, verifica unicidade
        if id_plataforma is not None:
            if id_plataforma in self.__ids_plataformas_existentes:
                raise ValueError(f"ID {id_plataforma} já existe para outra plataforma.")
            self.__ids_plataformas_existentes.add(id_plataforma)
        else:
            # Gera novo ID
            id_plataforma = self._encontrar_id_disponivel()
            self.__ids_plataformas_existentes.add(id_plataforma)

        # Cria e registra a plataforma
        plataforma = Plataforma(nome_plataforma, id_plataforma)
        self.__plataformas_registradas[nome] = plataforma
        return plataforma

    def obter_plataforma(self, nome_plataforma: str, id_plataforma: int = None):
        """
        Retorna uma plataforma pelo nome, cadastrando se não existir.
        Se o ID for conhecido (ex: vindo do CSV), deve ser passado para evitar conflitos.
        """
        nome = nome_plataforma.strip().lower()
        if nome in self.__plataformas_registradas:
            return self.__plataformas_registradas[nome]
        return self.cadastrar_plataforma(nome_plataforma, id_plataforma)

    def listar_plataformas(self):
        """
        Retorna uma lista de todas as plataformas cadastradas.
        """
        return list(self.__plataformas_registradas.values())

    def _carregar_interacoes_csv(self, caminho_arquivo: str):
        """
        Carrega dados brutos do CSV e retorna uma lista de dicionários.
        """
        interacoes = []
        try:
            with open(caminho_arquivo, encoding='utf-8') as f:
                leitor = csv.DictReader(f) # considera automaticamente que o arquivo possui cabeçalho
                for linha in leitor:
                    interacoes.append(linha)
        except Exception as e:
            print(f"Erro ao ler arquivo CSV: {e}")
        return interacoes



    def processar_interacoes_do_csv(self, caminho_arquivo: str):
        """
        Processa o CSV: instancia objetos, valida dados e vincula entidades.
        Garante que IDs de plataformas do CSV são respeitados para evitar duplicações.
        """
        linhas = self._carregar_interacoes_csv(caminho_arquivo)

        for num_linha, dados in enumerate(linhas, 1):
            try:
                # Coleta e valida campos essenciais
                id_conteudo = int(dados.get('id_conteudo', -1)) #define o valor padrão como -1 para facilitar a detecção de erro de valores ausentes ou inválidos
                nome_conteudo = dados.get('nome_conteudo', '').strip()
                nome_plataforma = dados.get('plataforma', '').strip()
                id_usuario = int(dados.get('id_usuario', -1))
                tipo_conteudo = dados.get('tipo_conteudo', 'video').strip().lower() #seta tipo_conteudo default como 'video', importante já que não temos a informação no csv original
                id_plataforma_csv = dados.get('id_plataforma', None) #no CSV atual o campo não existe, então será sempre None
                
                if id_plataforma_csv is not None and id_plataforma_csv != '':
                    try:
                        id_plataforma_csv = int(id_plataforma_csv)
                    except ValueError:
                        id_plataforma_csv = None
                else:
                    id_plataforma_csv = None

                # Validação dos campos obrigatórios
                if id_conteudo < 0 or not nome_conteudo or not nome_plataforma or id_usuario < 0:
                    print(f"[Linha {num_linha} ignorada]: Dados essenciais ausentes ou inválidos.")
                    continue

                # Obtém ou cadastra a plataforma, passando ID do CSV se disponível
                plataforma = self.obter_plataforma(nome_plataforma, id_plataforma_csv)

                # Cria ou recupera o conteúdo
                if id_conteudo not in self.__conteudos_registrados:
                    if tipo_conteudo == "video":
                        duracao = int(dados.get('duracao_total_video_seg', 0))
                        conteudo = Video(id_conteudo, nome_conteudo, duracao)
                    elif tipo_conteudo == "podcast":
                        duracao = int(dados.get('duracao_total_episodio_seg', 0))
                        conteudo = Podcast(id_conteudo, nome_conteudo, duracao)
                    elif tipo_conteudo == "artigo":
                        duracao = int(dados.get('tempo_leitura_estimado_seg', 0))
                        conteudo = Artigo(id_conteudo, nome_conteudo, duracao)
                    else:
                        print(f"[Linha {num_linha} ignorada]: Tipo de conteúdo desconhecido: {tipo_conteudo}.")
                        continue
                    self.__conteudos_registrados[id_conteudo] = conteudo
                else:
                    conteudo = self.__conteudos_registrados[id_conteudo]

                # Cria ou recupera o usuário
                if id_usuario not in self.__usuarios_registrados:
                    usuario = Usuario(id_usuario)
                    self.__usuarios_registrados[id_usuario] = usuario
                else:
                    usuario = self.__usuarios_registrados[id_usuario]

                # Cria a interação, validando dados
                try:
                    interacao = Interacao(dados, conteudo, plataforma)
                except ValueError as err:
                    print(f"[Linha {num_linha} ignorada]: Erro ao criar Interacao: {err}.")
                    continue

                # Vincula interação a conteúdo e usuário
                conteudo.adicionar_interacao(interacao)
                usuario.adicionar_interacao(interacao)

            except Exception as err: #erro genérico
                print(f"[Linha {num_linha} ignorada]: Erro inesperado: {err}.")


    # Métodos de análise e relatório

    def gerar_relatorio_engajamento_conteudos(self, top_n: int =None):
        """
        Gera e imprime relatório de engajamento dos conteúdos.
        """
        print("RELATÓRIO DE ENGAJAMENTO DOS CONTEÚDOS\n")
        conteudos = list(self.__conteudos_registrados.values()) # Obtém lista de todos os conteúdos cadastrados
        

        if top_n: # Se top_n definido, ordena os conteúdos pelo total de engajamento e limita a top_n
            conteudos_ordenados = sorted(conteudos, key=lambda c: c.calcular_total_interacoes_engajamento(), reverse=True)[:top_n]
        else: # ordena pelo id do conteúdo
            conteudos_ordenados = sorted(conteudos, key=lambda c: c.id_conteudo) 

        for conteudo in conteudos_ordenados: # Itera sobre os conteúdos para exibir as métricas
            metricas = conteudo.calcular_metricas()
            print(f"ID do Conteúdo: {conteudo.id_conteudo}")
            print(f"  Nome do Conteúdo: {conteudo.nome_conteudo}")
            print(f"  Total de Interações de Engajamento: {metricas.get('total_interacoes_engajamento', 0)}")
            print("  Contagem por Tipo de Interação:")
            for tipo, quantidade in metricas.get('contagem_por_tipo_interacao', {}).items(): # Itera sobre o dicionário que contém a contagem de cada tipo de interação
                print(f"    - {tipo}: {quantidade}")
            print(f"  Tempo Total de Consumo: {str(timedelta(seconds=int(metricas.get('tempo_total_consumo', 0))))}") # Exibe o tempo total de consumo formatado como horas:minutos:segundos
            print(f"  Média de Tempo de Consumo: {str(timedelta(seconds=int(metricas.get('media_tempo_consumo', 0))))}")
            print(f"  Percentual Médio Assistido: {(metricas.get('percentual_medio_assistido', 0))}")
            print("  Comentários:")
            comentarios = conteudo.listar_comentarios()
            if comentarios:  # Se houver comentários, imprime cada um deles
                for comentario in comentarios:
                    print(f"    - {comentario}")
            else:
                print("    Nenhum comentário registrado.")
            print("-" * 80)

    def gerar_relatorio_atividade_usuarios(self, top_n=None):
        """
        Imprime um relatório de atividade dos usuários, uma linha por interação.
        """
        print("RELATÓRIO DE ATIVIDADE DOS USUÁRIOS\n")
        usuarios = list(self.__usuarios_registrados.values())
        
        if top_n: # Se top_n definido, ordena usuários pelo número de interações (descendente)
            usuarios_ordenados = sorted(usuarios, key=lambda u: len(u.interacoes), reverse=True)[:top_n]
        else: # ordena pelo id_usuario
            usuarios_ordenados = sorted(usuarios, key=lambda u: u.id_usuario) 

        # Cabeçalho alinhando cada coluna para melhor leitura
        print(f"{'Usuário':<7} | {'Interação':<10} | {'Conteúdo':<28} | {'Plataforma':<14} | {'Data/Hora':<16} | {'Duração(s)':<10} | {'Comentário'}")
        print("-" * 150)

        for usuario in usuarios_ordenados: # Itera sobre os usuários para exibir suas métricas
            for interacao in usuario.interacoes: # Para cada interação do usuário, imprime uma linha detalhada
                nome_conteudo = getattr(interacao.conteudo_associado, 'nome_conteudo', 'N/A') # Obtém o nome do conteúdo associado à interação, ou 'N/A' se não existir
                nome_plataforma = getattr(interacao.plataforma_interacao, 'nome_plataforma', 'N/A')
                data_hora = interacao.timestamp_interacao.strftime("%Y-%m-%d %H:%M:%S") if hasattr(interacao, 'timestamp_interacao') else 'N/A' # Formata a data/hora da interação se disponível, senão 'N/A'
                duracao = interacao.watch_duration_seconds if getattr(interacao, 'tipo_interacao', '') == 'view_start' else "" # Exibe o tempo assistido apenas se a interação for do tipo 'view_start'
                comentario = interacao.comment_text if getattr(interacao, 'tipo_interacao', '') == 'comment' else ""

                # Imprime a linha formatada, alinhando cada campo conforme o cabeçalho
                print(f"{usuario.id_usuario:<7} | {interacao.tipo_interacao:<10} | {nome_conteudo:<28} | {nome_plataforma:<14} | {data_hora[:16]:<16} | {str(duracao):<10} | {comentario}")

    
    def identificar_top_conteudos(self, metrica, top_n=10):
        """
        Exibe o top N conteúdos ordenados por uma métrica escolhida.
        """

        metricas_map = { # Mapeamento de métricas para funções de cálculo
            "total_interacoes_engajamento": lambda c: c.calcular_total_interacoes_engajamento(),
            "visualizacoes": lambda c: c.calcular_contagem_por_tipo_interacao().get("view_start", 0),
            "likes": lambda c: c.calcular_contagem_por_tipo_interacao().get("like", 0),
            "comentarios": lambda c: c.calcular_contagem_por_tipo_interacao().get("comment", 0),
            "shares": lambda c: c.calcular_contagem_por_tipo_interacao().get("share", 0),
            "tempo_total_consumo": lambda c: str(timedelta(seconds=int(c.calcular_tempo_total_consumo()))),
            "media_tempo_consumo": lambda c: str(timedelta(seconds=int(c.calcular_media_tempo_consumo())))
        }
        nomes_metricas = { # Dicionário para nomes amigáveis das métricas, usado no cabeçalho do relatório
            "total_interacoes_engajamento": "TOTAL DE INTERAÇÕES DE ENGAJAMENTO",
            "visualizacoes": "VISUALIZAÇÕES",
            "likes": "CURTIDAS",
            "comentarios": "COMENTÁRIOS",
            "shares": "COMPARTILHAMENTOS",
            "tempo_total_consumo": "TEMPO TOTAL DE CONSUMO",
            "media_tempo_consumo": "MÉDIA DE TEMPO DE CONSUMO"
        }
        if metrica not in metricas_map:
            print(f"Métrica '{metrica}' não suportada.")
            return

        # Ordena os conteúdos pelo valor da métrica escolhida
        conteudos_ordenados = sorted(
            self.__conteudos_registrados.values(),
            key=metricas_map[metrica],
            reverse=True
        )

        print(f"TOP {top_n} CONTEÚDOS POR {nomes_metricas.get(metrica, metrica)}:\n")
        print(f"{'ID':<4} | {'Conteúdo':<30} | {nomes_metricas.get(metrica, metrica):<25}")
        print("-" * 65)
        for conteudo in conteudos_ordenados[:top_n]:
            valor = metricas_map[metrica](conteudo)
            print(f"{conteudo.id_conteudo:<4} | {conteudo.nome_conteudo:<30} | {valor:<25.2f}" if isinstance(valor, float) else f"{conteudo.id_conteudo:<4} | {conteudo.nome_conteudo:<30} | {valor:<25}")

    
    def gerar_relatorio_atividade_usuarios_resumido(self, top_n=None):
        """
        Imprime um relatório resumido da atividade dos usuários
        """
        print("RELATÓRIO RESUMIDO DE ATIVIDADE DOS USUÁRIOS\n")
        usuarios = list(self.__usuarios_registrados.values())
        usuarios_ordenados = sorted(usuarios, key=lambda u: u.id_usuario)

        if top_n: # ordena pelo total de interações se receber o argumento
            usuarios_ordenados = sorted(usuarios, key=lambda u: len(u.interacoes), reverse=True)[:top_n]
           
        print(f"{'Usuário':<8} | {'Interações':<11} | {'Comentários':<11} | {'Conteúdos':<9} | {'Plataformas Mais Frequentes':<40} | {'Views':<6} | {'Likes':<6} | {'Shares':<6}")
        print("-" * 140)

        for usuario in usuarios_ordenados:
            total_interacoes = len(usuario.interacoes)
            total_comentarios = len(usuario.filtrar_interacoes_por_tipo('comment'))
            total_conteudos = len(usuario.obter_conteudos_unicos())
            plataformas_frequentes = usuario.plataformas_mais_frequentes(top_n=3)
            plataformas_str = ', '.join(
            f"{p[0].nome_plataforma}({p[1]})" if hasattr(p[0], 'nome_plataforma') else str(p[0])
            for p in plataformas_frequentes
        )
            total_views = len(usuario.filtrar_interacoes_por_tipo('view_start'))
            total_likes = len(usuario.filtrar_interacoes_por_tipo('like'))
            total_shares = len(usuario.filtrar_interacoes_por_tipo('share'))

            print(f"{usuario.id_usuario:<8} | {total_interacoes:<11} | {total_comentarios:<11} | {total_conteudos:<9} | {plataformas_str:<40} | {total_views:<6} | {total_likes:<6} | {total_shares:<6}")    
   
    def buscar_interacoes_usuario(self):
        """
        Busca e exibe todas as interações de um usuário específico, ordenadas por data/hora.
        """
        print("BUSCA DE INTERAÇÕES DE UM USUÁRIO\n")
        try:
            id_usuario = int(input("Informe o ID do usuário: ").strip()) # Solicita o ID do usuário e converte para inteiro
        except ValueError:
            print("ID inválido.")
            return
        
        usuario = self.__usuarios_registrados.get(id_usuario)  # Busca o usuário no dicionário de usuários registrados

        if not usuario:
            print("Usuário não encontrado.")
            return

        print(f"\n{'Interação':<12} | {'Conteúdo':<28} | {'Plataforma':<12} | {'Data/Hora':<19} | {'Duração (s)':<11} | {'Comentário'}")
        print("-" * 110)

        interacoes_ordenadas = sorted(usuario.interacoes, key=lambda i: getattr(i, 'timestamp_interacao', '')) # Ordena as interações do usuário por timestamp (mais antigas primeiro)

        for interacao in interacoes_ordenadas:
            nome_conteudo = getattr(interacao.conteudo_associado, 'nome_conteudo', 'N/A')
            nome_plataforma = getattr(interacao.plataforma_interacao, 'nome_plataforma', 'N/A')
            data_hora = (interacao.timestamp_interacao.strftime("%Y-%m-%d %H:%M:%S")
                        if hasattr(interacao, 'timestamp_interacao') and interacao.timestamp_interacao else 'N/A')
            duracao = interacao.watch_duration_seconds if getattr(interacao, 'tipo_interacao', '') == 'view_start' else ""
            comentario = interacao.comment_text if getattr(interacao, 'tipo_interacao', '') == 'comment' else ""
            print(f"{interacao.tipo_interacao:<12} | {nome_conteudo:<28} | {nome_plataforma:<12} | {data_hora:<19} | {str(duracao):<11} | {comentario}")

    # Properties para acesso seguro
    @property
    def plataformas_registradas(self):
        return dict(self.__plataformas_registradas)

    @property
    def conteudos_registrados(self):
        return dict(self.__conteudos_registrados)

    @property
    def usuarios_registrados(self):
        return dict(self.__usuarios_registrados)