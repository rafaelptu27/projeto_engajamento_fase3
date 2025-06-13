from analise.sistema import SistemaAnaliseEngajamento # Importa a classe de análise implementada no módulo sistema
import os # Importa módulo para interações com o sistema operacional (utilizei para limpar o terminal)

# Cria o caminho para o arquivo CSV que contém as interações
csv = "interacoes_globo.csv"

def exibir_menu_relatorios(sistema):
    '''Função para exibir o menu de relatórios.'''
    while True:  # Loop do menu (até que o usuário decida sair)
        os.system('cls')  # Limpa o terminal
        # Exibe as opções do menu
        print("--- MENU DE RELATÓRIOS ---")
        print("1 - Relatório de Engajamento dos Conteúdos")
        print("2 - Top 10 Conteúdos por Métricas")
        print("3 - Relatório de Atividade dos Usuários (Resumo por usuário)")
        print("4 - Relatório de Atividade dos Usuários (Todas as interações)")
        print("5 - Buscar interações do Usuário")
        print("0 - Sair")
        opcao = input("\nEscolha uma opção: ").strip()  # captura a escolha do usuário

        # Ações baseadas na opção escolhida
        if opcao == "1":
            os.system('cls') # limpa o terminal
            sistema.gerar_relatorio_engajamento_conteudos()  # acessa a função que gera o relatório de engajamento na classe SistemaAnaliseEngajamento
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == "2":
            while True:  # Loop para usuário selecionar a métrica
                os.system('cls')
                print("--- TOP 10 CONTEÚDOS POR MÉTRICA ---\n\n Qual métrica deseja usar para ordenação?\n")
                print("1 - Total de Interações de Engajamento")
                print("2 - Total de visualizações")
                print("3 - Total de Curtidas")
                print("4 - Total de Comentários")
                print("5 - Total de Compartilhamentos")
                print("6 - Tempo Total de Consumo")
                print("7 - Média de Tempo de Consumo")
                print("0 - Voltar ao menu principal.")
                sub_opcao = input("\nEscolha uma opção: ").strip()

                # Ações baseadas na métrica escolhida
                if sub_opcao == "1":
                    os.system('cls')
                    sistema.identificar_top_conteudos("total_interacoes_engajamento", 10)  # Identifica top conteúdos
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "2":
                    os.system('cls')
                    sistema.identificar_top_conteudos("visualizacoes", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "3":
                    os.system('cls')
                    sistema.identificar_top_conteudos("likes", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "4":
                    os.system('cls')
                    sistema.identificar_top_conteudos("comentarios", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "5":
                    os.system('cls')
                    sistema.identificar_top_conteudos("shares", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "6":
                    os.system('cls')
                    sistema.identificar_top_conteudos("tempo_total_consumo", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "7":
                    os.system('cls')
                    sistema.identificar_top_conteudos("media_tempo_consumo", 10)
                    input("\nPressione Enter para voltar...")
                elif sub_opcao == "0":
                    break  # Sai do loop de métricas
                else:
                    print("Opção inválida. Tente novamente.")
                    input("\nPressione Enter para voltar...")
        elif opcao == "3":
            os.system('cls')
            sistema.gerar_relatorio_atividade_usuarios_resumido()  # acessa a função que gera relatório de atividades resumido por usuário
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == "4":
            os.system('cls')
            sistema.gerar_relatorio_atividade_usuarios()  # acessa função que gera relatório com todas as interações de todos os usuários
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == "5":
            os.system('cls')
            sistema.buscar_interacoes_usuario()  # acessa função que busca interações de um usuário específico
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == "0":
            print("\nSaindo do menu.\n")  
            break  # Sai do loop principal
        else:
            print("Opção inválida. Tente novamente.")
            input("\nPressione Enter para voltar ao menu...")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    sistema = SistemaAnaliseEngajamento()  # Cria uma instância do sistema de análise de engajamento
    sistema.processar_interacoes_do_csv(csv)  # Processa as interações do arquivo CSV
    input("\nCarga do arquivo concluída. Pressione Enter para acessar Menu de Relatórios")  # Mensagem de conclusão do processamento do CSV
    exibir_menu_relatorios(sistema)  # chama a função que exibe o menu de relatórios