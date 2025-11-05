import os
import sys
from dotenv import load_dotenv
from search import create_rag_chain
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def print_banner():
    print("=" * 60)
    print("SISTEMA DE BUSCA SEMÂNTICA COM LANGCHAIN")
    print("=" * 60)
    print("Digite 'sair' ou 'quit' para encerrar o chat")
    print("Digite 'ajuda' para ver comandos disponíveis")
    print("=" * 60)

def print_help():
    print("\nCOMANDOS DISPONÍVEIS:")
    print("• Digite sua pergunta normalmente")
    print("• 'sair' ou 'quit' - Encerra o chat")
    print("• 'ajuda' - Mostra esta mensagem")
    print("• 'limpar' ou 'clear' - Limpa a tela")
    print("\nDICAS:")
    print("• Faça perguntas específicas sobre o conteúdo do PDF")
    print("• O sistema só responde com base no documento carregado")
    print("• Se não houver informação no documento, você receberá uma mensagem padrão")
    print("=" * 60)
    print("Perguntas dentro do contexto:")
    print("=" * 60)
    print("PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?")
    print("RESPOSTA: O faturamento foi de 10 milhões de reais.")
    print("-" * 60)
    print("PERGUNTA: Qual o ano de fundação da Empresa SuperTechIABrazil?")
    print("RESPOSTA: A empresa foi fundada em 2020.")
    print("-" * 60)
    print("PERGUNTA: Quais empresas tem faturamento acima de 10 milhões de reais?")
    print("RESPOSTA: A empresa SuperTechIABrazil tem faturamento acima de 10 milhões de reais.")
    print("=" * 60)
    print("Perguntas fora do contexto:")
    print("=" * 60)
    print("PERGUNTA: Quantos clientes temos em 2024?")
    print("RESPOSTA: Não tenho informações necessárias para responder sua pergunta.")
    print("-" * 60)  
    print("PERGUNTA: Qual é a capital da França?")
    print("RESPOSTA: Não tenho informações necessárias para responder sua pergunta.")
    print("-" * 60)  

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print_banner()
    
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
      
    print("Faça sua pergunta:")
    print("-" * 60)
    while True:
        try:
            user_input = input("\nPERGUNTA: ").strip()
            
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
            
            print("Processando sua pergunta...")
            response = chain.invoke({"pergunta": user_input})
            
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