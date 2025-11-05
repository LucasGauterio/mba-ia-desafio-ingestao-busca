import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")+"_"+os.getenv("EMBEDDINGS_PROVIDER")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

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
        connection=DATABASE_URL,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        pre_delete_collection=True
    )
    
    logger.info(f"Indexando {len(chunks)} chunks no banco de dados...")
    logger.info(f"Collection: {PG_VECTOR_COLLECTION_NAME}")
    
    vector_store.add_documents(chunks)
    
    logger.info("Vector store criado com sucesso!")
    
    return vector_store

def ingest_pdf():
    try:
        if not os.path.exists(PDF_PATH):
            logger.error(f"Arquivo PDF não encontrado: {PDF_PATH}")
            return False
        
        embeddings = get_embeddings()
        documents = load_pdf(PDF_PATH)
        chunks = split_documents(documents)
        create_vector_store(embeddings, chunks)
        
        logger.info(f"Ingestão concluída: {len(documents)} páginas → {len(chunks)} chunks")
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"ERRO durante a ingestão: {str(e)}", exc_info=True)
        logger.error("=" * 60)
        return False

if __name__ == "__main__":
    success = ingest_pdf()
    if success:
        print("SUCESSO: Ingestão concluída com sucesso!")
    else:
        print("ERRO: Falha na ingestão. Verifique os logs para mais detalhes.")
        exit(1)