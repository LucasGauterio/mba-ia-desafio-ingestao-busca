# Desafio MBA Engenharia de Software com IA - Full Cycle

## Ingestão e Busca Semântica com LangChain e PostgreSQL

Este projeto implementa um sistema de busca semântica que permite fazer perguntas sobre o conteúdo de um PDF usando LangChain, PostgreSQL com extensão pgVector e modelos de IA.

## Funcionalidades

- **Ingestão de PDF**: Carrega e processa documentos PDF em chunks otimizados
- **Busca Semântica**: Utiliza embeddings para encontrar conteúdo relevante
- **Chat Interativo**: Interface CLI para fazer perguntas sobre o documento
- **Suporte Multi-Provider**: OpenAI e Google Gemini
- **Armazenamento Vetorial**: PostgreSQL com pgVector para busca eficiente

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- API Key da OpenAI ou Google Gemini
- Arquivo PDF para processar

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/LucasGauterio/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

### 2. Crie um ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

**Nota**: O projeto inclui `nest_asyncio` para resolver problemas de event loop ao usar o provedor Gemini. Esta dependência é necessária porque os embeddings do Google Generative AI usam operações assíncronas internamente e podem causar erros de event loop em thread pools.

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Provider de LLM e Embeddings (openai ou gemini)
LLM_PROVIDER=openai
EMBEDDINGS_PROVIDER=openai

# API Keys
OPENAI_API_KEY=sua_chave_openai_aqui
# GOOGLE_API_KEY=sua_chave_google_aqui

# Modelos OpenAI
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Modelos Google Gemini
GOOGLE_LLM_MODEL=gemini-2.0-flash-exp
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Configurações do banco
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_documents

# Arquivo PDF para processar
PDF_PATH=document.pdf
```

## Execução

### 1. Subir o banco de dados
```bash
docker compose up -d
```

Este comando irá:
- Subir o PostgreSQL 17 com extensão pgVector
- Criar automaticamente a extensão `vector` no banco (via serviço `bootstrap_vector_ext`)
- Aguardar o healthcheck do banco antes de inicializar a extensão

Aguarde alguns segundos para o banco inicializar completamente. O serviço `bootstrap_vector_ext` garante que a extensão pgVector esteja disponível antes de executar a ingestão.

### 2. Executar ingestão do PDF
```bash
python src/ingest.py
```

Este comando irá:
- Carregar o PDF especificado no caminho `PDF_PATH`
- Dividir em chunks de 1000 caracteres com overlap de 150
- Gerar embeddings usando o modelo configurado em `EMBEDDINGS_PROVIDER`
- Armazenar no PostgreSQL com pgVector na collection `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`
- Deletar a collection existente antes de criar uma nova (`pre_delete_collection=True`)

**Nota:** A collection no banco será nomeada automaticamente como `{PG_VECTOR_COLLECTION_NAME}_{EMBEDDINGS_PROVIDER}` para permitir múltiplos embeddings no mesmo banco.

### 3. Iniciar o chat
```bash
python src/chat.py
```

## Como usar o chat

Após iniciar o chat, você pode:

- Fazer perguntas sobre o conteúdo do PDF
- Usar comandos especiais:
  - `ajuda` ou `help` - Mostra comandos disponíveis e exemplos
  - `limpar` ou `clear` - Limpa a tela
  - `sair`, `quit` ou `exit` - Encerra o chat

O sistema utiliza RAG (Retrieval-Augmented Generation) para responder perguntas:
- Busca os documentos mais relevantes usando busca semântica (similarity search)
- Retorna os top 10 documentos mais relevantes (k=10)
- Usa o contexto encontrado para gerar a resposta com o LLM configurado
- Se a informação não estiver no contexto, retorna uma mensagem padrão

### Exemplos de perguntas:

**Perguntas dentro do contexto:**
```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Qual o ano de fundação da Empresa SuperTechIABrazil?
RESPOSTA: A empresa foi fundada em 2020.

PERGUNTA: Quais empresas tem faturamento acima de 10 milhões de reais?
RESPOSTA: A empresa SuperTechIABrazil tem faturamento acima de 10 milhões de reais.
```

**Perguntas fora do contexto:**
```
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Arquitetura

```
├── docker-compose.yml      # Configuração do PostgreSQL com pgVector
├── requirements.txt        # Dependências Python
├── .env.example           # Template de variáveis de ambiente
├── document.pdf           # PDF para processar
├── docs/                  # Documentação adicional (se houver)
├── src/
│   ├── ingest.py          # Script de ingestão do PDF
│   ├── search.py          # Lógica de busca semântica e RAG chain
│   └── chat.py            # Interface CLI do chat interativo
└── README.md              # Este arquivo
```

### Componentes do Sistema

1. **ingest.py**: Responsável por:
   - Carregar PDFs usando `PyPDFLoader`
   - Dividir documentos em chunks com `RecursiveCharacterTextSplitter`
   - Gerar embeddings (OpenAI ou Google Gemini)
   - Armazenar no PostgreSQL com pgVector

2. **search.py**: Contém:
   - Lógica de busca semântica (`similarity_search_with_score`)
   - Criação da RAG chain
   - Template de prompt configurável
   - Funções para obter LLM e embeddings baseados no provider

3. **chat.py**: Interface interativa:
   - Loop de chat com comandos especiais
   - Tratamento de erros e validações
   - Mensagens de ajuda e exemplos

## Configurações Avançadas

### Chunking
- **Tamanho do chunk**: 1000 caracteres
- **Overlap**: 150 caracteres
- **Separadores**: `["\n\n", "\n", " ", ""]`

### Busca
- **Número de resultados**: 10 (k=10) - configurável na função `search_documents()`
- **Método**: Similarity search com score (`similarity_search_with_score`)
- **Collection**: Nomeada como `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`
- **Score de relevância**: Mostrado no contexto formatado (quanto menor o score, mais relevante)

### Modelos Suportados

Os modelos são configuráveis via variáveis de ambiente:

#### OpenAI
- **Embeddings**: `OPENAI_EMBEDDING_MODEL` (padrão: `text-embedding-3-small`)
- **LLM**: `OPENAI_LLM_MODEL` (padrão: `gpt-4o-mini`)
- **Outros modelos disponíveis**: `text-embedding-3-large`, `text-embedding-ada-002`, `gpt-4`, `gpt-4-turbo`, etc.

#### Google Gemini
- **Embeddings**: `GOOGLE_EMBEDDING_MODEL` (padrão: `models/embedding-001`)
- **LLM**: `GOOGLE_LLM_MODEL` (padrão: `gemini-2.0-flash-exp`)
- **Outros modelos disponíveis**: `gemini-pro`, `gemini-1.5-pro`, etc.

### Sistema de Prompts

O sistema utiliza um template de prompt configurado em `search.py` que:
- Fornece contexto baseado nos documentos encontrados
- Estabelece regras claras para respostas apenas baseadas no contexto
- Inclui exemplos de perguntas fora do contexto
- Mantém temperatura do LLM em 0.1 para respostas mais determinísticas

## Solução de Problemas

### Erro de conexão com banco
```bash
# Verifique se o Docker está rodando
docker ps

# Reinicie o banco se necessário
docker compose down
docker compose up -d
```

### Erro de API Key
- Verifique se o arquivo `.env` está configurado corretamente
- Confirme se as API keys são válidas
- Verifique se tem créditos disponíveis

### Erro de ingestão
- Verifique se o arquivo PDF existe no caminho especificado em `PDF_PATH`
- Confirme se o banco está rodando e a extensão pgVector foi criada
- Verifique se as variáveis de ambiente estão configuradas corretamente
- Confirme que a API key do provider de embeddings está válida
- Verifique os logs para mais detalhes

### Erro ao iniciar o chat
- Execute primeiro `python src/ingest.py` para carregar os documentos
- Verifique se a collection existe no banco (nome: `${PG_VECTOR_COLLECTION_NAME}_${EMBEDDINGS_PROVIDER}`)
- Confirme que `LLM_PROVIDER` e `EMBEDDINGS_PROVIDER` estão configurados
- Verifique se as API keys estão corretas e têm créditos disponíveis

## Logs

O sistema utiliza o módulo `logging` do Python para gerar logs detalhados:
- **Nível padrão**: INFO
- **Logs de ingestão**: Mostram progresso, número de páginas, chunks criados e erros
- **Logs de busca**: Mostram queries executadas e resultados encontrados
- **Logs de chat**: Mostram interações do usuário e erros durante o processamento

Para ver logs mais detalhados, você pode modificar o nível de logging nos arquivos para `logging.DEBUG`.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é parte do desafio do MBA em Engenharia de Software com IA.