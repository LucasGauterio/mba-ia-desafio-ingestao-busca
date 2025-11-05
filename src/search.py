import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Fix for Gemini event loop issues in thread pools
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER")
LLM_PROVIDER = os.getenv("LLM_PROVIDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")+"_"+os.getenv("EMBEDDINGS_PROVIDER")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")

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
    if EMBEDDINGS_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    elif EMBEDDINGS_PROVIDER == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
        return GoogleGenerativeAIEmbeddings(
            model=GOOGLE_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
    else:
        raise ValueError(f"Provedor de embeddings não suportado: {EMBEDDINGS_PROVIDER}")

def get_llm():
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return ChatOpenAI(
            model=OPENAI_LLM_MODEL,
            openai_api_key=OPENAI_API_KEY,
            temperature=0.1
        )
    elif LLM_PROVIDER == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
        return ChatGoogleGenerativeAI(
            model=GOOGLE_LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1
        )
    else:
        raise ValueError(f"Provedor de LLM não suportado: {LLM_PROVIDER}")

def get_vector_store():
    embeddings = get_embeddings()
    return PGVector(
        embeddings=embeddings,
        connection=DATABASE_URL,
        collection_name=PG_VECTOR_COLLECTION_NAME
    )

def search_documents(query, k=10):
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)
        return results
    except Exception as e:
        logger.error(f"Erro ao buscar documentos: {str(e)}")
        return []

def format_context(documents):
    if not documents:
        return "Nenhum documento relevante encontrado."
    
    context_parts = []
    for i, (doc, score) in enumerate(documents):
        context_parts.append(f"Documento {i} (relevância: {score:.3f}):\n{doc.page_content}\n")
    
    return "\n".join(context_parts)

def create_rag_chain():
    try:
        llm = get_llm()
        
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        
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
    chain = create_rag_chain()
    if chain:
        print("SUCESSO: Sistema de busca inicializado com sucesso!")
        print("Teste: Qual é o conteúdo do documento?")
        result = chain.invoke({"pergunta": "Qual é o conteúdo do documento?"})
        print(f"Resposta: {result}")
    else:
        print("ERRO: Falha ao inicializar o sistema de busca.")