# Documentação: search.py

## Visão Geral

O script `search.py` implementa a lógica de busca semântica e criação da cadeia RAG (Retrieval-Augmented Generation). Ele fornece funções para buscar documentos relevantes no vector store e criar uma cadeia de processamento que combina busca vetorial com geração de texto usando LLMs.

## Funcionalidades Principais

1. **Busca Semântica**: Busca documentos relevantes usando similarity search
2. **Geração de Embeddings**: Suporte a múltiplos provedores de embeddings
3. **Criação de RAG Chain**: Monta a cadeia completa de RAG
4. **Formatação de Contexto**: Formata os documentos encontrados para o prompt
5. **Suporte Multi-Provider**: OpenAI e Google Gemini para embeddings e LLMs

## Dependências

```python
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging
```

**Nota sobre `nest_asyncio`**: O script aplica automaticamente `nest_asyncio` para resolver problemas de event loop ao usar o provedor Gemini durante a busca semântica. Os embeddings do Google Generative AI usam operações assíncronas internamente, e quando executados em thread pools durante `similarity_search_with_score` (usado pelo pgVector), podem causar o erro "There is no current event loop in thread". A aplicação de `nest_asyncio` permite que loops de eventos aninhados funcionem corretamente.

## Variáveis de Ambiente Necessárias

O script requer as seguintes variáveis de ambiente (definidas no arquivo `.env`):

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | URL de conexão com PostgreSQL | `postgresql://postgres:postgres@localhost:5432/rag` |
| `EMBEDDINGS_PROVIDER` | Provedor de embeddings (`openai` ou `gemini`) | `openai` |
| `LLM_PROVIDER` | Provedor de LLM (`openai` ou `gemini`) | `openai` |
| `OPENAI_API_KEY` | Chave de API da OpenAI | `sk-...` |
| `GOOGLE_API_KEY` | Chave de API do Google | `...` |
| `PG_VECTOR_COLLECTION_NAME` | Nome base da collection | `pdf_documents` |
| `GOOGLE_EMBEDDING_MODEL` | Modelo de embedding do Google | `models/embedding-001` |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embedding da OpenAI | `text-embedding-3-small` |
| `GOOGLE_LLM_MODEL` | Modelo LLM do Google | `gemini-2.0-flash-exp` |
| `OPENAI_LLM_MODEL` | Modelo LLM da OpenAI | `gpt-4o-mini` |

**Nota**: O nome final da collection será `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`.

## Template de Prompt

O sistema utiliza um template de prompt configurado que:

1. **Inclui o contexto**: Documentos relevantes encontrados na busca
2. **Define regras claras**: 
   - Responde apenas com base no contexto
   - Retorna mensagem padrão se informação não estiver no contexto
   - Não inventa informações
   - Não produz opiniões além do que está escrito
3. **Fornece exemplos**: Exemplos de perguntas fora do contexto e suas respostas esperadas

```python
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
# Retorna OpenAIEmbeddings(model=..., openai_api_key=...)
```

### 2. Função `get_llm()`

Retorna uma instância do modelo LLM baseado no provedor configurado.

**Parâmetros**: Nenhum (usa variáveis de ambiente)

**Retorno**: 
- `ChatOpenAI` se `LLM_PROVIDER == "openai"`
- `ChatGoogleGenerativeAI` se `LLM_PROVIDER == "gemini"`

**Configurações**:
- `temperature=0`: Garante respostas determinísticas e consistentes

**Exceções**:
- `ValueError`: Se `OPENAI_API_KEY` ou `GOOGLE_API_KEY` não estiverem configuradas
- `ValueError`: Se o provedor não for suportado

**Exemplo de uso**:
```python
llm = get_llm()
# Retorna ChatOpenAI(model=..., temperature=0, ...)
```

### 3. Função `get_vector_store()`

Cria e retorna uma instância do vector store conectado ao PostgreSQL.

**Parâmetros**: Nenhum (usa variáveis de ambiente)

**Retorno**: Instância de `PGVector` configurada

**Configuração**:
- `connection`: URL do banco de dados
- `collection_name`: `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`
- `embeddings`: Modelo de embeddings configurado

**Exemplo de uso**:
```python
vector_store = get_vector_store()
# Retorna PGVector conectado ao PostgreSQL
```

### 4. Função `search_documents(query, k=10)`

Realiza busca semântica de documentos relevantes no vector store.

**Parâmetros**:
- `query` (str): Consulta/pergunta do usuário
- `k` (int, opcional): Número de documentos a retornar (padrão: 10)

**Retorno**: Lista de tuplas `(document, score)` onde:
- `document`: Objeto `Document` do LangChain
- `score`: Score de similaridade (quanto menor, mais relevante)

**Comportamento**:
- Usa `similarity_search_with_score` para obter documentos e scores
- Retorna lista vazia em caso de erro (com log)

**Exemplo de uso**:
```python
results = search_documents("Qual o faturamento?", k=5)
# Retorna [(Document(...), 0.123), (Document(...), 0.456), ...]
```

**Tratamento de erros**:
- Captura exceções e loga com `ERROR`
- Retorna lista vazia em caso de erro

### 5. Função `format_context(documents)`

Formata os documentos encontrados em uma string de contexto para o prompt.

**Parâmetros**:
- `documents`: Lista de tuplas `(document, score)` retornada por `search_documents()`

**Retorno**: String formatada com o contexto

**Formato**:
```
Documento 0 (relevância: 0.123):
[conteúdo do documento]

Documento 1 (relevância: 0.456):
[conteúdo do documento]
...
```

**Exemplo de uso**:
```python
results = search_documents("pergunta")
context = format_context(results)
# Retorna string formatada com contexto
```

**Tratamento de casos especiais**:
- Se `documents` estiver vazio, retorna `"Nenhum documento relevante encontrado."`

### 6. Função `create_rag_chain()`

Cria e retorna a cadeia RAG completa configurada.

**Parâmetros**: Nenhum (usa variáveis de ambiente)

**Retorno**: 
- Objeto `RunnableSequence` (cadeia LangChain) se bem-sucedido
- `None` se ocorrer erro

**Estrutura da Cadeia**:
```python
{
    "contexto": lambda x: format_context(search_documents(x["pergunta"])),
    "pergunta": RunnablePassthrough()
}
| prompt
| llm
| StrOutputParser()
```

**Fluxo de execução**:
1. Recebe um dicionário com a chave `"pergunta"`
2. Busca documentos relevantes usando `search_documents()`
3. Formata o contexto usando `format_context()`
4. Preenche o template de prompt com contexto e pergunta
5. Envia para o LLM
6. Retorna a resposta como string

**Exemplo de uso**:
```python
chain = create_rag_chain()
if chain:
    response = chain.invoke({"pergunta": "Qual o faturamento?"})
    print(response)
```

**Tratamento de erros**:
- Captura exceções e loga com `ERROR`
- Retorna `None` em caso de erro

### 7. Função `search_prompt(question=None)`

Função de conveniência para buscar uma pergunta ou retornar a cadeia.

**Parâmetros**:
- `question` (str, opcional): Pergunta a ser processada. Se `None`, retorna apenas a cadeia.

**Retorno**:
- Se `question` é `None`: Retorna a cadeia RAG
- Se `question` é fornecida: Retorna a resposta como string
- Em caso de erro: Retorna string de erro

**Exemplo de uso**:
```python
# Retornar apenas a cadeia
chain = search_prompt()

# Processar uma pergunta diretamente
response = search_prompt("Qual o faturamento?")
```

**Tratamento de erros**:
- Retorna `"Erro ao inicializar o sistema de busca."` se cadeia não for criada
- Retorna `"Erro ao processar sua pergunta. Tente novamente."` em caso de erro no processamento

## Execução

### Execução direta

```bash
python src/search.py
```

Quando executado diretamente, o script:
1. Cria a cadeia RAG
2. Testa com uma pergunta padrão
3. Exibe o resultado

### Execução como módulo

```python
from src.search import create_rag_chain, search_prompt

# Opção 1: Criar cadeia e usar
chain = create_rag_chain()
response = chain.invoke({"pergunta": "Qual o faturamento?"})

# Opção 2: Usar função de conveniência
response = search_prompt("Qual o faturamento?")
```

## Exemplo de Saída

**Sucesso na inicialização**:
```
INFO:root: Sistema de busca inicializado
SUCESSO: Sistema de busca inicializado com sucesso!
Teste: Qual é o conteúdo do documento?
Resposta: [resposta do LLM baseada no contexto]
```

**Erro**:
```
ERROR:root: Erro ao criar cadeia RAG: ...
ERRO: Falha ao inicializar o sistema de busca.
```

## Arquitetura RAG

O sistema implementa uma arquitetura RAG (Retrieval-Augmented Generation) com os seguintes componentes:

```
┌─────────────┐
│   Pergunta  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Embedding Query    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Similarity Search  │  (k=10 documentos)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Format Context     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Prompt Template    │  (contexto + pergunta)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│      LLM            │  (GPT-4o-mini ou Gemini)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Resposta          │
└─────────────────────┘
```

## Tratamento de Erros Comuns

### 1. Collection não encontrada
```
Erro ao buscar documentos: relation "pdf_documents_openai" does not exist
```
**Solução**: Execute primeiro `python src/ingest.py` para criar a collection

### 2. Erro de conexão com banco
```
Erro ao buscar documentos: could not connect to server
```
**Solução**: 
- Verifique se o PostgreSQL está rodando
- Verifique a `DATABASE_URL`
- Aguarde alguns segundos após iniciar o banco

### 3. API Key não configurada
```
ValueError: OPENAI_API_KEY não encontrada nas variáveis de ambiente
```
**Solução**: Configure as API keys no arquivo `.env`

### 4. Provedor não suportado
```
ValueError: Provedor de embeddings não suportado: anthropic
```
**Solução**: Use apenas `openai` ou `gemini`

### 5. Erro de event loop com Gemini
```
ERROR:search:Erro ao buscar documentos: There is no current event loop in thread 'ThreadPoolExecutor-1_0'.
```
**Causa**: Este erro ocorre especificamente com o provedor Gemini durante a busca semântica (`similarity_search_with_score`). Os embeddings do Google Generative AI usam operações assíncronas internamente, e quando executados em thread pools (usados pelo pgVector durante a busca), não há um event loop disponível.

**Solução**: O script já aplica automaticamente `nest_asyncio.apply()` na inicialização para resolver este problema. Certifique-se de que a dependência está instalada:

```bash
pip install nest_asyncio==1.6.0
```

O código tenta importar e aplicar `nest_asyncio` automaticamente, mas se a dependência não estiver instalada, o erro pode ocorrer. A aplicação é feita de forma condicional, então não afeta o uso com outros provedores.

**Nota**: Este erro não ocorre durante a ingestão (`ingest.py`), apenas durante a busca semântica em `search.py`.

## Considerações Importantes

1. **Independência de Provedores**: O provedor de embeddings pode ser diferente do provedor de LLM. Por exemplo, você pode usar embeddings do OpenAI com LLM do Gemini (ou vice-versa).

2. **Temperature Zero**: O LLM é configurado com `temperature=0.1` para garantir respostas determinísticas e consistentes, ideal para perguntas factuais sobre documentos.

3. **Número de Resultados**: O padrão é buscar os top 10 documentos (`k=10`). Você pode ajustar esse valor na chamada de `search_documents()`.

4. **Score de Relevância**: O score de similaridade retornado pelo pgVector é uma distância (quanto menor, mais relevante). O score é incluído no contexto formatado para referência.

5. **Mensagem Padrão**: O template de prompt instrui o LLM a retornar uma mensagem padrão quando a informação não está no contexto, evitando alucinações.

6. **Event Loop com Gemini**: O script aplica automaticamente `nest_asyncio` para resolver problemas de event loop específicos do provedor Gemini durante a busca semântica. Esta correção é aplicada na inicialização do módulo e não afeta outros provedores. O erro ocorre apenas durante `similarity_search_with_score`, não durante a ingestão.

## Integração com Outros Scripts

Este script é usado por:

- **`chat.py`**: Usa `create_rag_chain()` para criar a cadeia RAG e processar perguntas do usuário

## Melhorias Futuras

Possíveis melhorias para o script:

1. Suporte a diferentes estratégias de busca (MMR, filtros, etc.)
2. Configuração de `k` via variável de ambiente
3. Suporte a metadados na busca
4. Cache de buscas frequentes
5. Métricas de relevância (MRR, NDCG)
6. Suporte a re-ranking de resultados
7. Configuração de prompt via arquivo externo
8. Suporte a múltiplas collections
9. Histórico de conversação
10. Streaming de respostas

