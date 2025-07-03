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
from estruturas_dados.fila import Fila
from estruturas_dados.arvore_binaria_busca import ArvoreBinariaBusca
import os


class SistemaAnaliseEngajamento:
    """
    Classe de orquestração do sistema de análise de engajamento.
    Gerencia plataformas, conteúdos, usuários e processa interações.
    """

    def __init__(self):
        self._fila_interacoes_brutas = Fila() # Fila para armazenar interações brutas do CSV
        self._arvore_conteudos = ArvoreBinariaBusca() # Árvore para armazenar conteúdos
        self._arvore_usuarios = ArvoreBinariaBusca()   # Árvore para armazenar usuários
        self._plataformas_registradas = {}  # Dicionário para armazenar plataformas registradas
  
    def _validar_interacao(self, interacao):
        """Executa todas as validações necessárias para uma interação."""

        # Validação de id_conteudo
        id_conteudo = interacao.get('id_conteudo', -1) #define o valor padrão como -1 para facilitar a detecção de erro de valores ausentes ou inválidos
        if not id_conteudo or not id_conteudo.isdigit() or int(id_conteudo) < 0:
            raise ValueError(f"ID de conteúdo inválido: {id_conteudo}")
        
        # Validação do nome do conteúdo
        if not interacao.get('nome_conteudo') or interacao['nome_conteudo'].strip() == "":
            raise ValueError("Nome do conteúdo ausente")

        # Validação de id_usuario
        id_usuario = interacao.get('id_usuario', -1)
        if not id_usuario or not id_usuario.isdigit() or int(id_usuario) < 0:
            raise ValueError(f"ID de usuário inválido: {id_usuario}")
               
        # Validação de timestamp
        if not interacao.get('timestamp_interacao'):
            raise ValueError(f"Timestamp ausente")
        
        # Validação de plataforma
        if not interacao.get('plataforma') or interacao['plataforma'].strip() == "":
            raise ValueError("Nome da plataforma ausente")
        
        # Validação do tipo de interação
        if not interacao.get('tipo_interacao') or interacao['tipo_interacao'].strip() == "":
            raise ValueError("Tipo da interação ausente")
        
        # Validação do tipo de conteúdo
        tipo_conteudo = interacao.get('tipo_conteudo', 'video').strip().lower()  # Define 'video' como padrão
        if tipo_conteudo not in ['video', 'podcast', 'artigo']:
            raise ValueError(f"Tipo de conteúdo inválido: {tipo_conteudo}. Deve ser 'video', 'podcast' ou 'artigo'.")
        
        return True
    
    def _carregar_interacoes_csv(self, caminho_arquivo: str):
        """
        Carrega dados brutos do CSV
        """
        try:
            with open(caminho_arquivo, encoding='utf-8') as f:
                leitor = csv.DictReader(f) # considera automaticamente que o arquivo possui cabeçalho
                for linha in leitor:
                    try:
                        self._validar_interacao(linha) # Valida linha antes de enfileirar
                        self._fila_interacoes_brutas.enfileirar(linha)
                    except ValueError as e:
                        print(f"[AVISO] Linha ignorada: {e}")
        except (FileNotFoundError, PermissionError) as e:
            print(f"Erro crítico ao carregar CSV: {e}")
            raise
        self.processar_interacoes_da_fila()  # Processa as interações após carregar o CSV

    def processar_interacoes_da_fila(self):
        """
        Processa as interações armazenadas na fila, criando ou atualizando conteúdos, usuários e plataformas.
        Vincula interações a conteúdos e usuários.
        """
        while not self._fila_interacoes_brutas.is_empty(): # Enquanto houver interações na fila
            dados = self._fila_interacoes_brutas.desenfileirar() # Obtém a próxima interação da fila
            try: # Valida e processa a interação
                id_conteudo = int(dados['id_conteudo'])
                id_usuario = int(dados['id_usuario'])
                nome_plataforma = dados['plataforma']
                nome_conteudo = dados['nome_conteudo'].strip()

                # Conteúdo
                conteudo = self._arvore_conteudos.buscar(id_conteudo) # Busca conteúdo na árvore
                if conteudo is None: # Se não encontrar, cria um novo conteúdo
                    tipo_conteudo = dados.get('tipo_conteudo', 'video').strip().lower()
                    duracao = int(dados.get('duracao_total_seg', 0))
                    if tipo_conteudo == "video":
                        conteudo = Video(id_conteudo, nome_conteudo, duracao)
                    elif tipo_conteudo == "podcast":
                        conteudo = Podcast(id_conteudo, nome_conteudo, duracao)
                    else:
                        conteudo = Artigo(id_conteudo, nome_conteudo, duracao)
                    self._arvore_conteudos.inserir(id_conteudo, conteudo) # Insere o conteúdo na árvore

                # Usuário
                usuario = self._arvore_usuarios.buscar(id_usuario)
                if usuario is None:
                    usuario = Usuario(id_usuario)
                    self._arvore_usuarios.inserir(id_usuario, usuario) # Insere o usuário na árvore

                # Plataforma
                if nome_plataforma not in self._plataformas_registradas:
                    plataforma = self.obter_plataforma(nome_plataforma) # Obtém ou cadastra a plataforma
                else:
                    plataforma = self._plataformas_registradas[nome_plataforma]

                # Interação
                try:
                    interacao = Interacao(dados, conteudo, plataforma)
                except ValueError as err:
                    print(f"[Linha ignorada]: Erro ao criar Interacao: {err}.")
                    continue

                # Vincula interação a conteúdo, usuário e plataforma
                conteudo.adicionar_interacao(interacao)
                usuario.adicionar_interacao(interacao)
                plataforma.adicionar_interacao(interacao)

            except Exception as e:
                print(f"[ERRO] Falha ao processar interação: {e}") 

    # Métodos de gerenciamento de plataforma

    def cadastrar_plataforma(self, nome_plataforma: str):
        """
        Cadastra uma nova plataforma se não existir. Retorna o objeto Plataforma.
        """
        nome = nome_plataforma.strip().lower()
        if nome in self._plataformas_registradas: # Se já existe por nome, retorna a plataforma já registrada
            return self._plataformas_registradas[nome]

        # Cria e registra a plataforma
        plataforma = Plataforma(nome_plataforma)
        self._plataformas_registradas[nome] = plataforma
        return plataforma

    def obter_plataforma(self, nome_plataforma: str):
        """
        Retorna uma plataforma pelo nome, cadastrando se não existir.
        """
        nome = nome_plataforma.strip().lower()
        if nome in self._plataformas_registradas:
            return self._plataformas_registradas[nome]
        return self.cadastrar_plataforma(nome_plataforma)

    def listar_plataformas(self):
        """
        Retorna uma lista de todas as plataformas cadastradas.
        """
        return list(self._plataformas_registradas.values()) 

    def listar_conteudos(self):
        """
        Retorna uma lista de todos os conteúdos cadastrados.
        """
        return self._arvore_conteudos.percurso_em_ordem()

    def listar_usuarios(self):
        """
        Retorna uma lista de todos os usuários cadastrados.
        """
        return self._arvore_usuarios.percurso_em_ordem()

    def listar_plataformas(self):
        """
        Retorna uma lista de todas as plataformas registradas, ordenadas por nome.
        """
        plataformas = list(self._plataformas_registradas.values())
        algoritmo = 'insertion' if len(plataformas) <= 20 else 'quick'
        self._ordenar_lista(plataformas, algoritmo=algoritmo, key=lambda p: p.nome_plataforma.lower(), reverse=False)
        return plataformas  # Retorna a lista de plataformas ordenadas      
           
    
    # Algoritmos de ordenação

    def _ordenar_lista(self, lista, algoritmo, key=None, reverse=False):
        """
        Ordena uma lista usando quicksort ou insertion sort.
        """
        if algoritmo == 'quick':
            self._quicksort(lista, 0, len(lista) - 1, key, reverse)
        else:
            self._insertion_sort(lista, key, reverse)
            
    def _quicksort(self, lista, inicio, fim, key=None, reverse=False):
        if inicio < fim:
            p = self._particionar(lista, inicio, fim, key, reverse)
            self._quicksort(lista, inicio, p - 1, key, reverse)
            self._quicksort(lista, p + 1, fim, key, reverse)
    
    def _particionar(self, lista, inicio, fim, key=None, reverse=False):
        pivo = key(lista[fim])
        i = inicio
        for j in range(inicio, fim):
            if (key(lista[j]) > pivo if reverse else key(lista[j]) < pivo):
                lista[i], lista[j] = lista[j], lista[i]
                i += 1
        lista[i], lista[fim] = lista[fim], lista[i]
        return i
    
    def _insertion_sort(self, lista, key=None, reverse=False):
        for i in range(1, len(lista)):
            atual = lista[i]
            j = i - 1
            while j >= 0 and (key(lista[j]) < key(atual) if reverse else key(lista[j]) > key(atual)):
                lista[j + 1] = lista[j]
                j -= 1
            lista[j + 1] = atual

    def identificar_top_n(self, lista, top_n, metrica):
        """
        Ordena o top N de uma lista por uma métrica escolhida.
        """
        algoritmo = 'insertion' if len(lista) <= 20 else 'quick'
        self._ordenar_lista(lista, algoritmo=algoritmo, key=metrica, reverse=True)
        return lista[:top_n] # Retorna o top N


    # Métodos de análise e relatório

    def gerar_relatorio_engajamento_conteudos(self, top_n=10):
        """
        Gera relatórios de engajamento dos conteúdos cadastrados.
        Permite ao usuário escolher entre diferentes métricas de engajamento.
        """
        conteudos = self._arvore_conteudos.percurso_em_ordem() # Obtém lista de todos conteúdos cadastrados

        metricas_map = { # Mapeamento de métricas para funções de cálculo e nomes amigáveis usados no cabeçalho do relatório
            "total_interacoes_engajamento": {'func': lambda c: c.calcular_total_interacoes_engajamento(),'nome':'TOTAL DE INTERAÇÕES DE ENGAJAMENTO'},
            "visualizacoes": {'func': lambda c: c.calcular_contagem_por_tipo_interacao().get("view_start", 0),'nome':'VISUALIZAÇÕES'},
            "likes": {'func': lambda c: c.calcular_contagem_por_tipo_interacao().get("like", 0),'nome':'CURTIDAS'},
            "comentarios": {'func': lambda c: c.calcular_contagem_por_tipo_interacao().get("comment", 0),'nome':'COMENTÁRIOS'},
            "shares": {'func': lambda c: c.calcular_contagem_por_tipo_interacao().get("share", 0),'nome':'COMPARTILHAMENTOS'},
            "tempo_total_consumo": {'func': lambda c: str(timedelta(seconds=int(c.calcular_tempo_total_consumo()))),'nome':'TEMPO TOTAL DE CONSUMO'},
            "media_tempo_consumo": {'func': lambda c: str(timedelta(seconds=int(c.calcular_media_tempo_consumo()))),'nome':'MÉDIA DE TEMPO DE CONSUMO'}
        }

        while True:  # Loop para usuário selecionar a métrica
                os.system('cls') # limpa o terminal
                print("--- RELATÓRIOS DE ENGAJAMENTO DOS CONTEÚDOS ---\n")
                print("1 - Relatório geral de engajamento dos conteúdos")
                print("2 - Top 10 Interações de Engajamento")
                print("3 - Top 10 Visualizações")
                print("4 - Top 10 Curtidas")
                print("5 - Top 10 Comentários")
                print("6 - Top 10 Compartilhamentos")
                print("7 - Top 10 Tempo Total de Consumo")
                print("8 - Top 10 Média de Tempo de Consumo")
                print("0 - Voltar ao menu principal.")
                sub_opcao = input("\nEscolha uma opção: ").strip()

                # Ações baseadas na métrica escolhida
                if sub_opcao == "1":
                    os.system('cls')

                    print("--- RELATÓRIO GERAL DE ENGAJAMENTO DOS CONTEÚDOS ---\n")
                    for conteudo in conteudos:
                        metricas = conteudo.calcular_metricas()
                        print(f"ID do Conteúdo: {conteudo.id_conteudo}")
                        print(f"  Nome do Conteúdo: {conteudo.nome_conteudo}")
                        print(f"  Total de Interações de Engajamento: {metricas.get('total_interacoes_engajamento', 0)}")
                        print("  Contagem por Tipo de Interação:")
                        for tipo, quantidade in metricas.get('contagem_por_tipo_interacao', {}).items():
                            print(f"    - {tipo}: {quantidade}")
                        print(f"  Tempo Total de Consumo: {str(timedelta(seconds=int(metricas.get('tempo_total_consumo', 0))))}")
                        print(f"  Média de Tempo de Consumo: {str(timedelta(seconds=int(metricas.get('media_tempo_consumo', 0))))}")
                        print(f"  Percentual Médio Assistido: {metricas.get('percentual_medio_assistido', 0)}")
                        print("  Comentários:")
                        comentarios = conteudo.listar_comentarios()
                        if comentarios:
                            for comentario in comentarios:
                                print(f"    - {comentario}")
                        else:
                            print("    Nenhum comentário registrado.")
                        print("-" * 80)
                    input("\nPressione Enter para voltar...")
            
                elif sub_opcao in ["2", "3", "4", "5", "6", "7", "8"]:
                    os.system('cls')
                    conteudos_ordenados = conteudos.copy()  # Cria ou reseta a lista ordenada para o estado original
                    metrica_keys = { # Mapeamento de opções para chaves de métrica
                        "2": "total_interacoes_engajamento",
                        "3": "visualizacoes",
                        "4": "likes",
                        "5": "comentarios",
                        "6": "shares",
                        "7": "tempo_total_consumo",
                        "8": "media_tempo_consumo"
                    }
                    metrica = metrica_keys[sub_opcao]
                    top_conteudos = self.identificar_top_n(conteudos_ordenados, top_n, metricas_map[metrica]['func'])

                    print(f"TOP {top_n} CONTEÚDOS POR {metricas_map[metrica]['nome']}:\n")
                    print(f"{'ID':<4} | {'Conteúdo':<30} | {metricas_map[metrica]['nome']:<25}")
                    print("-" * 65)
                    for conteudo in top_conteudos:
                        valor = metricas_map[metrica]['func'](conteudo)
                        print(f"{conteudo.id_conteudo:<4} | {conteudo.nome_conteudo:<30} | {valor:<25.2f}" if isinstance(valor, float) else f"{conteudo.id_conteudo:<4} | {conteudo.nome_conteudo:<30} | {valor:<25}")
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "0":
                    break  # Sai do loop de métricas
                else:
                    print("Opção inválida. Tente novamente.")
                    input("\nPressione Enter para voltar...")

    def gerar_relatorio_atividade_usuarios(self, top_n=10):
        """
        Gera relatórios de atividade dos usuários cadastrados.
        Permite ao usuário escolher entre diferentes métricas de atividade.
        """
        usuarios = self._arvore_usuarios.percurso_em_ordem()

        metricas_map = {
            'quantidade_interacoes': {'func': lambda u: len(u.interacoes), 'nome': 'INTERAÇÕES'},
            'quantidade_conteudos': {'func': lambda u: len(u.obter_conteudos_unicos()), 'nome': 'CONTEÚDOS'},
            'tempo_total_assistido': {'func': lambda u: u.calcular_tempo_total_assistido(), 'nome': 'TEMPO TOTAL ASSISTIDO'}
        }

        while True:  # Loop para usuário selecionar a métrica
                os.system('cls') # limpa o terminal
                print("--- RELATÓRIOS DE ENGAJAMENTO DOS USUÁRIOS ---\n")
                print("1 - Relatório geral com todas interações dos usuários")
                print("2 - Buscar interações por usuário")
                print("3 - Top 10 por por quantidade de interações")
                print("4 - Top 10 por quantidade de conteúdos distintos")
                print("5 - Top 10 por tempo total assistido")
                print("0 - Voltar ao menu principal.")
                sub_opcao = input("\nEscolha uma opção: ").strip()

                # Ações baseadas na métrica escolhida
                if sub_opcao == "1":
                    os.system('cls')

                    print("--- LISTA DE TODAS AS INTERAÇÕES POR USUÁRIO ---\n")
                    print(f"{'Usuário':<8} | {'Interação':<12} | {'Conteúdo':<28} | {'Plataforma':<14} | {'Data/Hora':<16} | {'Duração(s)':<10} | {'Comentário'}")
                    print("-" * 150)
                    for usuario in usuarios:
                        interacoes_ordenadas = sorted(
                            usuario.interacoes,
                            key=lambda i: getattr(i, 'timestamp_interacao', '')
                        )
                        for idx, interacao in enumerate(interacoes_ordenadas):
                            nome_conteudo = getattr(interacao.conteudo_associado, 'nome_conteudo', 'N/A')
                            nome_plataforma = getattr(interacao.plataforma_interacao, 'nome_plataforma', 'N/A')
                            data_hora = (interacao.timestamp_interacao.strftime("%Y-%m-%d %H:%M")
                                        if hasattr(interacao, 'timestamp_interacao') and interacao.timestamp_interacao else 'N/A')
                            duracao = interacao.watch_duration_seconds if getattr(interacao, 'tipo_interacao', '') == 'view_start' else ""
                            comentario = interacao.comment_text if getattr(interacao, 'tipo_interacao', '') == 'comment' else ""
                            print(f"{usuario.id_usuario if idx == 0 else '':<8} | {interacao.tipo_interacao:<12} | {nome_conteudo:<28} | {nome_plataforma:<14} | {data_hora:<16} | {str(duracao):<10} | {comentario}")
                        print("-" * 150)  # Linha para separar blocos de usuários
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == '2':
                    os.system('cls')
                    self.buscar_interacoes_usuario()  # acessa função que busca interações de um usuário específico
                    input("\nPressione Enter para voltar...")
                elif sub_opcao in ('3', '4', '5'):
                    os.system('cls')
                    usuarios_ordenados = usuarios.copy()  # Cria ou reseta a lista para o estado original
                    metrica_keys = {
                    "3": "quantidade_interacoes",
                    "4": "quantidade_conteudos",
                    "5": "tempo_total_assistido",
                    }
                    metrica = metrica_keys[sub_opcao]
                    top_usuarios = self.identificar_top_n(usuarios_ordenados, top_n, metricas_map[metrica]['func'])

                    print(f"TOP {top_n} USUÁRIOS POR {metricas_map[metrica]['nome']}:\n")
                    print(f"{'Usuário':<7} | {'Interações':<10} | {'Comentários':<11} | {'Conteúdos':<9} | {'Tempo Total Assistido':<24} | {'Plataformas Mais Frequentes':<35} | {'Views':<7} | {'Likes':<7} | {'Shares':<7}")
                    print("-" * 140)
                    for usuario in top_usuarios:
                        plataformas_str = ', '.join(
                            f"{p[0].nome_plataforma}({p[1]})" if hasattr(p[0], 'nome_plataforma') else str(p[0])
                            for p in usuario.plataformas_mais_frequentes(top_n=3)
                        )
                        print(f"{usuario.id_usuario:<7} | "
                            f"{len(usuario.interacoes):<10} | "
                            f"{len(usuario.filtrar_interacoes_por_tipo('comment')):<11} | "
                            f"{len(usuario.obter_conteudos_unicos()):<9} | "
                            f"{str(timedelta(seconds=int(usuario.calcular_tempo_total_assistido()))):<24} | "
                            f"{plataformas_str:<35} | "
                            f"{len(usuario.filtrar_interacoes_por_tipo('view_start')):<7} | "
                            f"{len(usuario.filtrar_interacoes_por_tipo('like')):<7} | "
                            f"{len(usuario.filtrar_interacoes_por_tipo('share')):<7}")
                    print("-" * 140)
                    input("\nPressione Enter para voltar...")

                elif sub_opcao == "0":
                    break  # Sai do loop de métricas
                else:
                    print("Opção inválida. Tente novamente.")
                    input("\nPressione Enter para voltar...")
    
    def buscar_interacoes_usuario(self):
        """
        Busca e exibe todas as interações de um usuário específico, ordenadas por data/hora.
        """
        try:
            id_usuario = int(input("Informe o ID do usuário: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        usuario = self._arvore_usuarios.buscar(id_usuario)
        if not usuario:
            print("Usuário não encontrado.")
            return
        
        interacoes = usuario.interacoes.copy()
        algoritmo = 'insertion' if len(interacoes) <= 20 else 'quick'
        self._ordenar_lista(interacoes, algoritmo=algoritmo,  key=lambda i: getattr(i, 'timestamp_interacao', ''), reverse=False)

        print(f"\n{'Interação':<12} | {'Conteúdo':<28} | {'Plataforma':<14} | {'Data/Hora':<19} | {'Duração (s)':<11} | {'Comentário'}")
        print("-" * 150)
        for interacao in interacoes:
            nome_conteudo = getattr(interacao.conteudo_associado, 'nome_conteudo', 'N/A')
            nome_plataforma = getattr(interacao.plataforma_interacao, 'nome_plataforma', 'N/A')
            data_hora = (interacao.timestamp_interacao.strftime("%Y-%m-%d %H:%M:%S")
                        if hasattr(interacao, 'timestamp_interacao') and interacao.timestamp_interacao else 'N/A')
            duracao = interacao.watch_duration_seconds if getattr(interacao, 'tipo_interacao', '') == 'view_start' else ""
            comentario = interacao.comment_text if getattr(interacao, 'tipo_interacao', '') == 'comment' else ""
            print(f"{interacao.tipo_interacao:<12} | {nome_conteudo:<28} | {nome_plataforma:<14} | {data_hora:<19} | {str(duracao):<11} | {comentario}")

        print("-" * 150)
    
    def gerar_relatorio_engajamento_plataformas(self, top_n=10):
        plataformas = self.listar_plataformas()  # Obtém lista de todas plataformas cadastradas

        metricas_map = {
            'quantidade_interacoes': {'func': lambda p: p.calcular_total_interacoes_engajamento(), 'nome': 'INTERAÇÕES DE ENGAJAMENTO'},
            'tempo_medio_consumo': {'func': lambda p: p.calcular_media_tempo_consumo(), 'nome': 'TEMPO MÉDIO DE CONSUMO'},
            'tempo_total_assistido': {'func': lambda p: p.calcular_tempo_total_consumo(), 'nome': 'TEMPO TOTAL DE CONSUMO'}
        }

        while True:
            os.system('cls')
            print("--- RELATÓRIO DE ENGAJAMENTO DAS PLATAFORMAS ---\n")
            print("1 - Listar todas as plataformas registradas")
            print("2 - Top 10 por engajamento")
            print("3 - Top 10 por tempo médio de consumo")
            print("4 - Top 10 por tempo total de consumo")
            print("0 - Voltar ao menu principal")
            sub_opcao = input("\nEscolha uma opção: ").strip()

            if sub_opcao == "1":
                os.system('cls')

                print("--- LISTA DE TODAS PLATAFORMAS REGISTRADAS ---\n")
                for plataforma in plataformas:
                    print(f"- {plataforma.nome_plataforma}")
                print("-" * 60)
                input("\nPressione Enter para voltar...")

            elif sub_opcao in ('2', '3', '4'):
                    os.system('cls')
                    plataformas_ordenadas = plataformas.copy()  # Cria ou reseta a lista para o estado original
                    metrica_keys = {
                    "2": "quantidade_interacoes",
                    "3": "tempo_medio_consumo",
                    "4": "tempo_total_assistido",
                    }
                    metrica = metrica_keys[sub_opcao]
                    top_plataformas = self.identificar_top_n(plataformas_ordenadas, top_n, metricas_map[metrica]['func'])

                    print(f"TOP {top_n} PLATAFORMAS POR {metricas_map[metrica]['nome']}:\n")
                    print(f"{'Plataforma':<15} | {'Interações de Engajamento':<25} | {'Tempo Médio de Consumo':<22} | {'Tempo Total Assistido':<25}")
                    print("-" * 140)
                    for plataforma in top_plataformas:
                        print(f"{plataforma.nome_plataforma:<15} | "
                            f"{plataforma.calcular_total_interacoes_engajamento():<25} | "
                            f"{str(timedelta(seconds=int(plataforma.calcular_media_tempo_consumo()))):<22} | "
                            f"{str(timedelta(seconds=int(plataforma.calcular_tempo_total_consumo()))):<25}")
                    print("-" * 140)
                    input("\nPressione Enter para voltar...")

            elif sub_opcao == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")
                input("\nPressione Enter para voltar...")
    
    @property
    def plataformas_registradas(self):
        return dict(self._plataformas_registradas)
    
    @property
    def conteudos_registrados(self):
        return {c.id_conteudo: c for c in self._arvore_conteudos.percurso_em_ordem()}

    @property
    def usuarios_registrados(self):
        return {u.id_usuario: u for u in self._arvore_usuarios.percurso_em_ordem()}