# Documentação dos Scripts

Este diretório contém a documentação detalhada de cada script na pasta `src/`.

## Estrutura da Documentação

- **[ingest.md](./ingest.md)**: Documentação do script `ingest.py`
  - Processo de ingestão de PDFs
  - Geração de embeddings
  - Armazenamento no PostgreSQL com pgVector

- **[search.md](./search.md)**: Documentação do script `search.py`
  - Busca semântica
  - Criação da cadeia RAG
  - Integração com LLMs

- **[chat.md](./chat.md)**: Documentação do script `chat.py`
  - Interface CLI interativa
  - Processamento de perguntas
  - Comandos e tratamento de erros

## Visão Geral do Sistema

O sistema de busca semântica é composto por três scripts principais que trabalham em conjunto:

```
┌─────────────┐
│  ingest.py  │  Carrega PDFs e cria vector store
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  search.py  │  Implementa busca semântica e RAG chain
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   chat.py   │  Interface interativa para o usuário
└─────────────┘
```

## Fluxo de Trabalho

1. **Ingestão** (`ingest.py`):
   - Carrega o PDF
   - Divide em chunks
   - Gera embeddings
   - Armazena no PostgreSQL

2. **Busca** (`search.py`):
   - Busca documentos relevantes
   - Formata contexto
   - Cria cadeia RAG
   - Processa perguntas

3. **Chat** (`chat.py`):
   - Interface interativa
   - Recebe perguntas do usuário
   - Usa a cadeia RAG para gerar respostas
   - Exibe resultados

## Documentação Detalhada

Para informações detalhadas sobre cada script, consulte os arquivos correspondentes:

- [Documentação do ingest.py](./ingest.md)
- [Documentação do search.py](./search.md)
- [Documentação do chat.py](./chat.md)

## Dependências Entre Scripts

```
ingest.py
  └─► Depende de: variáveis de ambiente, PostgreSQL, APIs de embeddings
  
search.py
  └─► Depende de: variáveis de ambiente, PostgreSQL, APIs de embeddings/LLM
  └─► Usa: collection criada por ingest.py
  
chat.py
  └─► Depende de: search.py (importa create_rag_chain)
  └─► Usa: cadeia RAG criada por search.py
```

## Ordem de Execução Recomendada

1. Configure as variáveis de ambiente no arquivo `.env`
2. Inicie o PostgreSQL: `docker compose up -d`
3. Execute a ingestão: `python src/ingest.py`
4. Inicie o chat: `python src/chat.py`

## Variáveis de Ambiente Comuns

Todos os scripts compartilham as seguintes variáveis de ambiente:

- `DATABASE_URL`: URL de conexão com PostgreSQL
- `EMBEDDINGS_PROVIDER`: Provedor de embeddings (`openai` ou `gemini`)
- `LLM_PROVIDER`: Provedor de LLM (`openai` ou `gemini`)
- `OPENAI_API_KEY`: Chave de API da OpenAI
- `GOOGLE_API_KEY`: Chave de API do Google
- `PG_VECTOR_COLLECTION_NAME`: Nome base da collection

## Notas Importantes

### Suporte ao Provedor Gemini

O script `search.py` aplica automaticamente `nest_asyncio` para resolver problemas de event loop ao usar o provedor Gemini durante a busca. Os embeddings do Google Generative AI usam operações assíncronas internamente, e quando executados em thread pools (usados pelo pgVector durante `similarity_search_with_score`), podem causar o erro "There is no current event loop in thread".

**Solução**: Certifique-se de que `nest_asyncio` está instalado:
```bash
pip install nest_asyncio==1.6.0
```

O código aplica automaticamente `nest_asyncio.apply()` na inicialização do módulo `search.py`, permitindo que operações assíncronas do Google Generative AI funcionem corretamente em thread pools durante a busca semântica.

## Suporte

Para problemas ou dúvidas sobre os scripts, consulte:

1. A documentação específica de cada script
2. O README.md principal do projeto
3. Os logs de erro (configurados em nível INFO)
4. As mensagens de erro exibidas pelos scripts
5. A seção de "Tratamento de Erros Comuns" em cada documentação específica

