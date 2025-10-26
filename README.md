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

- Python 3.8+
- Docker e Docker Compose
- API Key da OpenAI ou Google Gemini
- Arquivo PDF para processar

## Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
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

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Para OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui
LLM_PROVIDER=openai
EMBEDDINGS_PROVIDER=openai

# Para Google Gemini (alternativa)
# GOOGLE_API_KEY=sua_chave_google_aqui
# LLM_PROVIDER=gemini
# EMBEDDINGS_PROVIDER=gemini

# Configurações do banco
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PDF_PATH=document.pdf
```

## Execução

### 1. Subir o banco de dados
```bash
docker compose up -d
```

Aguarde alguns segundos para o banco inicializar completamente.

### 2. Executar ingestão do PDF
```bash
python src/ingest.py
```

Este comando irá:
- Carregar o PDF especificado
- Dividir em chunks de 1000 caracteres com overlap de 150
- Gerar embeddings usando o modelo configurado
- Armazenar no PostgreSQL com pgVector

### 3. Iniciar o chat
```bash
python src/chat.py
```

## Como usar o chat

Após iniciar o chat, você pode:

- Fazer perguntas sobre o conteúdo do PDF
- Usar comandos especiais:
  - `ajuda` - Mostra comandos disponíveis
  - `limpar` - Limpa a tela
  - `sair` - Encerra o chat

### Exemplos de perguntas:
```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Arquitetura

```
├── docker-compose.yml      # Configuração do PostgreSQL com pgVector
├── requirements.txt        # Dependências Python
├── .env.example           # Template de variáveis de ambiente
├── document.pdf           # PDF para processar
├── src/
│   ├── ingest.py          # Script de ingestão do PDF
│   ├── search.py          # Lógica de busca semântica
│   └── chat.py            # Interface CLI do chat
└── README.md              # Este arquivo
```

## Configurações Avançadas

### Chunking
- **Tamanho do chunk**: 1000 caracteres
- **Overlap**: 150 caracteres
- **Separadores**: `["\n\n", "\n", " ", ""]`

### Busca
- **Número de resultados**: 10 (k=10)
- **Método**: Similarity search com score

### Modelos Suportados

#### OpenAI
- **Embeddings**: `text-embedding-3-small`
- **LLM**: `gpt-4o-mini`

#### Google Gemini
- **Embeddings**: `models/embedding-001`
- **LLM**: `gemini-2.0-flash-exp`

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
- Verifique se o arquivo PDF existe
- Confirme se o banco está rodando
- Verifique os logs para mais detalhes

## Logs

O sistema gera logs detalhados para facilitar o debug:
- Logs de ingestão mostram progresso e erros
- Logs de busca mostram queries e resultados
- Logs de chat mostram interações do usuário

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é parte do desafio do MBA em Engenharia de Software com IA.