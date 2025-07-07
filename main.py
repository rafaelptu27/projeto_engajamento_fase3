from analise.sistema import SistemaAnaliseEngajamento # Importa a classe de análise implementada no módulo sistema
import os # Importa módulo para interações com o sistema operacional (utilizei para limpar o terminal)

# Cria o caminho para o arquivo CSV que contém as interações
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interacoes_globo.csv")

def exibir_menu_relatorios(sistema):
    """
    Função para exibir o menu de relatórios.
    """
    while True:  # Loop do menu (até que o usuário decida sair)
        os.system('cls')  # Limpa o terminal
        # Exibe as opções do menu
        print("--- MENU DE RELATÓRIOS ---")
        print("1 - Relatórios de Engajamento dos Conteúdos")
        print("2 - Relatórios de Engajamento dos Usuários")
        print("3 - Relatórios de Engajamento das Plataformas")
        print("0 - Sair")
        opcao = input("\nEscolha uma opção: ").strip()  # captura a escolha do usuário

        # Ações baseadas na opção escolhida
        if opcao == "1":
            os.system('cls') # limpa o terminal
            sistema.gerar_relatorio_engajamento_conteudos() # acessa a função que gera relatórios de engajamento dos conteúdos
        elif opcao == "2":
            os.system('cls')
            sistema.gerar_relatorio_atividade_usuarios() # acessa a função que gera relatórios de engajamento dos usuários
        elif opcao == "3":
            os.system('cls')
            sistema.gerar_relatorio_engajamento_plataformas() # acessa a função que gera relatórios de atividades das plataformas
        elif opcao == "0":
            print("\nSaindo do menu.\n")  
            break  # Sai do loop principal
        else:
            print("Opção inválida. Tente novamente.")
            input("\nPressione Enter para voltar ao menu...")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    os.system('cls')  # Limpa o terminal ao iniciar o script
    sistema = SistemaAnaliseEngajamento()  # Cria uma instância do sistema de análise de engajamento
    sistema._carregar_interacoes_csv(csv_path)  # Processa as interações do arquivo CSV
    input("\nCarga do arquivo concluída. Pressione Enter para acessar Menu de Relatórios")  # Mensagem de conclusão do processamento do CSV
    exibir_menu_relatorios(sistema)  # chama a função que exibe o menu de relatórios