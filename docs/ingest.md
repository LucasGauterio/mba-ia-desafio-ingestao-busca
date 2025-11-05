# Documentação: ingest.py

## Visão Geral

O script `ingest.py` é responsável pelo processo de ingestão de documentos PDF no sistema de busca semântica. Ele realiza o carregamento, processamento, divisão em chunks e armazenamento vetorial dos documentos no PostgreSQL com extensão pgVector.

## Funcionalidades Principais

1. **Carregamento de PDF**: Lê arquivos PDF usando PyPDFLoader
2. **Divisão em Chunks**: Divide documentos em fragmentos menores para melhor indexação
3. **Geração de Embeddings**: Cria representações vetoriais do texto usando modelos de embeddings
4. **Armazenamento Vetorial**: Armazena os embeddings no PostgreSQL com pgVector

## Dependências

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
import logging
```


## Variáveis de Ambiente Necessárias

O script requer as seguintes variáveis de ambiente (definidas no arquivo `.env`):

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `PDF_PATH` | Caminho para o arquivo PDF a ser processado | `document.pdf` |
| `DATABASE_URL` | URL de conexão com PostgreSQL | `postgresql://postgres:postgres@localhost:5432/rag` |
| `EMBEDDINGS_PROVIDER` | Provedor de embeddings (`openai` ou `gemini`) | `openai` |
| `OPENAI_API_KEY` | Chave de API da OpenAI (se usar OpenAI) | `sk-...` |
| `GOOGLE_API_KEY` | Chave de API do Google (se usar Gemini) | `...` |
| `PG_VECTOR_COLLECTION_NAME` | Nome base da collection no banco | `pdf_documents` |
| `GOOGLE_EMBEDDING_MODEL` | Modelo de embedding do Google | `models/embedding-001` |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embedding da OpenAI | `text-embedding-3-small` |

**Nota**: O nome final da collection será `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}` para permitir múltiplos provedores no mesmo banco.

## Configurações Padrão

```python
CHUNK_SIZE = 1000        # Tamanho de cada chunk em caracteres
CHUNK_OVERLAP = 150      # Sobreposição entre chunks em caracteres
```

## Estrutura do Código

### 1. Função `get_embeddings()`

Retorna uma instância do modelo de embeddings baseado no provedor configurado.

**Parâmetros**: Nenhum (usa variáveis de ambiente)

**Retorno**: 
- `OpenAIEmbeddings` se `EMBEDDINGS_PROVIDER == "openai"`
- `GoogleGenerativeAIEmbeddings` se `EMBEDDINGS_PROVIDER == "gemini"`

**Exceções**:
- `ValueError`: Se `OPENAI_API_KEY` ou `GOOGLE_API_KEY` não estiverem configuradas
- `ValueError`: Se o provedor não for suportado

**Exemplo de uso**:
```python
embeddings = get_embeddings()
# Retorna OpenAIEmbeddings ou GoogleGenerativeAIEmbeddings
```

### 2. Função `load_pdf(pdf_path)`

Carrega um arquivo PDF e retorna uma lista de documentos.

**Parâmetros**:
- `pdf_path` (str): Caminho para o arquivo PDF

**Retorno**: Lista de objetos `Document` do LangChain

**Exceções**:
- `FileNotFoundError`: Se o arquivo PDF não existir

**Exemplo de uso**:
```python
documents = load_pdf("document.pdf")
# Retorna lista de Document objects, um por página
```

**Logging**: 
- `INFO`: Loga o caminho do PDF sendo carregado
- `INFO`: Loga o número de páginas carregadas

### 3. Função `split_documents(documents)`

Divide documentos em chunks menores usando `RecursiveCharacterTextSplitter`.

**Parâmetros**:
- `documents` (list): Lista de objetos `Document` do LangChain

**Retorno**: Lista de objetos `Document` divididos em chunks

**Configuração do TextSplitter**:
- `chunk_size`: 1000 caracteres
- `chunk_overlap`: 150 caracteres
- `separators`: `["\n\n", "\n", " ", ""]` (prioridade de separação)

**Exemplo de uso**:
```python
chunks = split_documents(documents)
# Retorna lista de Document objects divididos em chunks
```

**Logging**:
- `INFO`: Loga o início da divisão
- `INFO`: Loga o número total de chunks criados

### 4. Função `create_vector_store(embeddings, chunks)`

Cria e popula o vector store no PostgreSQL com os chunks processados.

**Parâmetros**:
- `embeddings`: Instância do modelo de embeddings
- `chunks` (list): Lista de chunks de documentos a serem indexados

**Retorno**: Instância de `PGVector` configurada

**Comportamento**:
- Deleta a collection existente antes de criar uma nova (`pre_delete_collection=True`)
- Cria a collection com nome `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`
- Adiciona todos os chunks ao banco de dados

**Exemplo de uso**:
```python
vector_store = create_vector_store(embeddings, chunks)
# Cria/atualiza a collection no PostgreSQL
```

**Logging**:
- `INFO`: Loga o início da criação do vector store
- `INFO`: Loga o número de chunks sendo indexados
- `INFO`: Loga o nome da collection
- `INFO`: Loga sucesso na criação

### 5. Função `ingest_pdf()`

Função principal que orquestra todo o processo de ingestão.

**Parâmetros**: Nenhum (usa variáveis de ambiente)

**Retorno**: 
- `True` se a ingestão foi bem-sucedida
- `False` se ocorreu algum erro

**Fluxo de execução**:
1. Verifica se o arquivo PDF existe
2. Obtém o modelo de embeddings configurado
3. Carrega o PDF
4. Divide em chunks
5. Cria o vector store no PostgreSQL

**Exemplo de uso**:
```python
success = ingest_pdf()
if success:
    print("Ingestão concluída!")
```

**Tratamento de erros**:
- Captura todas as exceções e loga com `exc_info=True`
- Retorna `False` em caso de erro
- Loga mensagens de erro formatadas com separadores

**Logging**:
- `INFO`: Logs de progresso de cada etapa
- `ERROR`: Logs detalhados em caso de erro (com traceback)

## Execução

### Execução direta

```bash
python src/ingest.py
```

### Execução como módulo

```python
from src.ingest import ingest_pdf

success = ingest_pdf()
```

## Exemplo de Saída

**Sucesso**:
```
INFO: Carregando PDF: document.pdf
INFO: PDF carregado com 5 páginas
INFO: Dividindo documentos em chunks...
INFO: Documentos divididos em 23 chunks
INFO: Criando vector store no PostgreSQL...
INFO: Indexando 23 chunks no banco de dados...
INFO: Collection: pdf_documents_openai
INFO: Vector store criado com sucesso!
INFO: Ingestão concluída: 5 páginas → 23 chunks
SUCESSO: Ingestão concluída com sucesso!
```

**Erro**:
```
ERROR: Arquivo PDF não encontrado: document.pdf
ERRO: Falha na ingestão. Verifique os logs para mais detalhes.
```

## Tratamento de Erros Comuns

### 1. Arquivo PDF não encontrado
```
ERROR: Arquivo PDF não encontrado: document.pdf
```
**Solução**: Verifique se o arquivo existe no caminho especificado em `PDF_PATH`

### 2. API Key não configurada
```
ValueError: OPENAI_API_KEY não encontrada nas variáveis de ambiente
```
**Solução**: Configure a variável `OPENAI_API_KEY` ou `GOOGLE_API_KEY` no arquivo `.env`

### 3. Erro de conexão com banco
```
Erro ao conectar com PostgreSQL
```
**Solução**: 
- Verifique se o PostgreSQL está rodando (`docker compose up -d`)
- Verifique se a `DATABASE_URL` está correta
- Aguarde alguns segundos após iniciar o banco para a extensão pgVector ser criada

### 4. Provedor não suportado
```
ValueError: Provedor de embeddings não suportado: anthropic
```
**Solução**: Use apenas `openai` ou `gemini` como `EMBEDDINGS_PROVIDER`


## Considerações Importantes

1. **Deleção de Collection**: O script deleta a collection existente antes de criar uma nova. Isso significa que executar o script novamente substituirá todos os dados anteriores.

2. **Nomenclatura de Collection**: A collection é nomeada como `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}` para permitir usar múltiplos provedores de embeddings no mesmo banco.

3. **Chunking**: O tamanho e overlap dos chunks são fixos no código. Para ajustar, modifique as constantes `CHUNK_SIZE` e `CHUNK_OVERLAP`.

4. **Logging**: O nível de logging é configurado como `INFO`. Para logs mais detalhados, altere para `DEBUG` na linha 11.

5. **Extensão pgVector**: O banco PostgreSQL deve ter a extensão `vector` instalada. O docker-compose.yml deve incluir um serviço para criar essa extensão automaticamente.

## Integração com Outros Scripts

Este script é usado como passo inicial antes de executar `chat.py`. O fluxo típico é:

1. Execute `ingest.py` para carregar os documentos
2. Execute `chat.py` para fazer perguntas sobre os documentos

O script `search.py` é usado por `chat.py` para buscar nos documentos indexados por este script.

## Melhorias Futuras

Possíveis melhorias para o script:

1. Suporte a múltiplos arquivos PDF
2. Opção de não deletar collection existente (append mode)
3. Configuração de chunking via variáveis de ambiente
4. Suporte a outros formatos de arquivo (DOCX, TXT, etc.)
5. Barra de progresso durante a indexação
6. Validação de integridade após ingestão
7. Suporte a metadados customizados

