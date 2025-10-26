import os
import sys
from dotenv import load_dotenv
from search import create_rag_chain
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def print_banner():
    """Exibe o banner do sistema"""
    print("=" * 60)
    print("SISTEMA DE BUSCA SEMÂNTICA COM LANGCHAIN")
    print("=" * 60)
    print("Digite 'sair' ou 'quit' para encerrar o chat")
    print("Digite 'ajuda' para ver comandos disponíveis")
    print("=" * 60)

def print_help():
    """Exibe a ajuda do sistema"""
    print("\nCOMANDOS DISPONÍVEIS:")
    print("• Digite sua pergunta normalmente")
    print("• 'sair' ou 'quit' - Encerra o chat")
    print("• 'ajuda' - Mostra esta mensagem")
    print("• 'limpar' ou 'clear' - Limpa a tela")
    print("\nDICAS:")
    print("• Faça perguntas específicas sobre o conteúdo do PDF")
    print("• O sistema só responde com base no documento carregado")
    print("• Se não houver informação no documento, você receberá uma mensagem padrão")
    print("-" * 60)

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Função principal do chat"""
    print_banner()
    
    # Inicializar o sistema de busca
    print("Inicializando sistema de busca...")
    chain = create_rag_chain()
    
    if not chain:
        print("ERRO: Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        print("\nPOSSÍVEIS SOLUÇÕES:")
        print("1. Verifique se o banco de dados PostgreSQL está rodando")
        print("2. Execute primeiro: python src/ingest.py")
        print("3. Verifique as variáveis de ambiente no arquivo .env")
        print("4. Verifique se as API keys estão configuradas corretamente")
        return
    
    print("Sistema inicializado com sucesso!")
    print("\nChat iniciado! Faça sua pergunta:")
    print("-" * 60)
    
    # Loop principal do chat
    while True:
        try:
            # Obter input do usuário
            user_input = input("\nPERGUNTA: ").strip()
            
            # Verificar comandos especiais
            if user_input.lower() in ['sair', 'quit', 'exit']:
                print("\nAté logo! Chat encerrado.")
                break
            elif user_input.lower() in ['ajuda', 'help']:
                print_help()
                continue
            elif user_input.lower() in ['limpar', 'clear']:
                clear_screen()
                print_banner()
                continue
            elif not user_input:
                print("AVISO: Por favor, digite uma pergunta.")
                continue
            
            # Processar pergunta
            print("Processando sua pergunta...")
            response = chain.invoke({"pergunta": user_input})
            
            # Exibir resposta
            print(f"\nRESPOSTA: {response}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nChat interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            logger.error(f"Erro durante o chat: {str(e)}")
            print(f"\nERRO: Erro ao processar sua pergunta: {str(e)}")
            print("Tente novamente ou digite 'ajuda' para ver os comandos disponíveis.")
            print("-" * 60)

if __name__ == "__main__":
    main()