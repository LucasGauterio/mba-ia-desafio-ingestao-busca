import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rag")
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "openai")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def get_embeddings():
    """Retorna o modelo de embeddings baseado na configuração"""
    if EMBEDDINGS_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )
    elif EMBEDDINGS_PROVIDER == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
    else:
        raise ValueError(f"Provedor de embeddings não suportado: {EMBEDDINGS_PROVIDER}")

def get_llm():
    """Retorna o modelo de LLM baseado na configuração"""
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=OPENAI_API_KEY,
            temperature=0
        )
    elif LLM_PROVIDER == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )
    else:
        raise ValueError(f"Provedor de LLM não suportado: {LLM_PROVIDER}")

def get_vector_store():
    """Retorna o vector store conectado ao PostgreSQL"""
    embeddings = get_embeddings()
    return PGVector(
        embeddings=embeddings,
        connection_string=DATABASE_URL,
        collection_name="pdf_documents"
    )

def search_documents(query, k=10):
    """Busca documentos similares no vector store"""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)
        return results
    except Exception as e:
        logger.error(f"Erro ao buscar documentos: {str(e)}")
        return []

def format_context(documents):
    """Formata os documentos encontrados como contexto"""
    if not documents:
        return "Nenhum documento relevante encontrado."
    
    context_parts = []
    for i, (doc, score) in enumerate(documents, 1):
        context_parts.append(f"Documento {i} (relevância: {score:.3f}):\n{doc.page_content}\n")
    
    return "\n".join(context_parts)

def create_rag_chain():
    """Cria a cadeia RAG para busca e resposta"""
    try:
        # Obter LLM
        llm = get_llm()
        
        # Criar prompt template
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        
        # Criar chain
        chain = (
            {
                "contexto": lambda x: format_context(search_documents(x["pergunta"])),
                "pergunta": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain
    except Exception as e:
        logger.error(f"Erro ao criar cadeia RAG: {str(e)}")
        return None

def search_prompt(question=None):
    """Função principal de busca - mantida para compatibilidade"""
    if question is None:
        return create_rag_chain()
    
    chain = create_rag_chain()
    if not chain:
        return "Erro ao inicializar o sistema de busca."
    
    try:
        result = chain.invoke({"pergunta": question})
        return result
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {str(e)}")
        return "Erro ao processar sua pergunta. Tente novamente."

if __name__ == "__main__":
    # Teste da função de busca
    chain = create_rag_chain()
    if chain:
        print("SUCESSO: Sistema de busca inicializado com sucesso!")
        print("Teste: Qual é o conteúdo do documento?")
        result = chain.invoke({"pergunta": "Qual é o conteúdo do documento?"})
        print(f"Resposta: {result}")
    else:
        print("ERRO: Falha ao inicializar o sistema de busca.")