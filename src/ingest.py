import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rag")
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

def get_embeddings():
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

def load_pdf(pdf_path):
    logger.info(f"Carregando PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    logger.info(f"PDF carregado com {len(documents)} páginas")
    return documents

def split_documents(documents):
    logger.info("Dividindo documentos em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Documentos divididos em {len(chunks)} chunks")
    return chunks

def create_vector_store(embeddings, chunks):
    logger.info("Criando vector store no PostgreSQL...")
    
    vector_store = PGVector(
        embeddings=embeddings,
        connection_string=DATABASE_URL,
        collection_name="pdf_documents",
        pre_delete_collection=True
    )
    
    logger.info("Adicionando chunks ao vector store...")
    vector_store.add_documents(chunks)
    
    logger.info("Vector store criado com sucesso!")
    return vector_store

def ingest_pdf():
    try:
        if not os.path.exists(PDF_PATH):
            logger.error(f"Arquivo PDF não encontrado: {PDF_PATH}")
            return False
        
        logger.info(f"Usando provedor de embeddings: {EMBEDDINGS_PROVIDER}")
        embeddings = get_embeddings()
        
        documents = load_pdf(PDF_PATH)
        
        chunks = split_documents(documents)
        
        vector_store = create_vector_store(embeddings, chunks)
        
        logger.info("Ingestão concluída com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a ingestão: {str(e)}")
        return False

if __name__ == "__main__":
    success = ingest_pdf()
    if success:
        print("SUCESSO: Ingestão concluída com sucesso!")
    else:
        print("ERRO: Falha na ingestão. Verifique os logs para mais detalhes.")
        exit(1)