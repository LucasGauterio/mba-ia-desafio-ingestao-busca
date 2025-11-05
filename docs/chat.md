# Documentação: chat.py

## Visão Geral

O script `chat.py` implementa a interface de linha de comando (CLI) interativa para o sistema de busca semântica. Ele permite que os usuários façam perguntas sobre o conteúdo dos documentos PDF processados, usando uma interface conversacional amigável.

## Funcionalidades Principais

1. **Interface Interativa**: Loop de chat com entrada do usuário
2. **Processamento de Perguntas**: Integração com a cadeia RAG para gerar respostas
3. **Comandos Especiais**: Comandos para ajuda, limpeza de tela e saída
4. **Tratamento de Erros**: Tratamento robusto de exceções e validações
5. **Mensagens Informativas**: Banner, ajuda e exemplos de uso

## Dependências

```python
import os
import sys
from dotenv import load_dotenv
from search import create_rag_chain
import logging
```

## Variáveis de Ambiente

O script não requer variáveis de ambiente próprias, mas depende das variáveis configuradas para os scripts `search.py` e `ingest.py`:

- `DATABASE_URL`
- `EMBEDDINGS_PROVIDER`
- `LLM_PROVIDER`
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY`
- `PG_VECTOR_COLLECTION_NAME`
- Modelos de embeddings e LLMs

## Estrutura do Código

### 1. Função `print_banner()`

Exibe o banner inicial do sistema com informações sobre o sistema e comandos básicos.

**Parâmetros**: Nenhum

**Retorno**: Nenhum (apenas imprime na tela)

**Exemplo de saída**:
```
============================================================
SISTEMA DE BUSCA SEMÂNTICA COM LANGCHAIN
============================================================
Digite 'sair' ou 'quit' para encerrar o chat
Digite 'ajuda' para ver comandos disponíveis
============================================================
```

### 2. Função `print_help()`

Exibe uma mensagem de ajuda completa com comandos disponíveis e exemplos de perguntas.

**Parâmetros**: Nenhum

**Retorno**: Nenhum (apenas imprime na tela)

**Conteúdo**:
- Lista de comandos disponíveis
- Dicas de uso
- Exemplos de perguntas dentro do contexto
- Exemplos de perguntas fora do contexto

**Exemplo de saída**:
```
COMANDOS DISPONÍVEIS:
• Digite sua pergunta normalmente
• 'sair' ou 'quit' - Encerra o chat
• 'ajuda' - Mostra esta mensagem
• 'limpar' ou 'clear' - Limpa a tela

DICAS:
• Faça perguntas específicas sobre o conteúdo do PDF
• O sistema só responde com base no documento carregado
• Se não houver informação no documento, você receberá uma mensagem padrão
...
```

### 3. Função `clear_screen()`

Limpa a tela do terminal de forma multiplataforma.

**Parâmetros**: Nenhum

**Retorno**: Nenhum

**Comportamento**:
- Windows: Executa `cls`
- Linux/Mac: Executa `clear`

**Exemplo de uso**:
```python
clear_screen()  # Limpa a tela
```

### 4. Função `main()`

Função principal que orquestra todo o fluxo do chat interativo.

**Parâmetros**: Nenhum

**Retorno**: Nenhum

**Fluxo de execução**:

1. **Inicialização**:
   - Exibe o banner inicial
   - Carrega a cadeia RAG usando `create_rag_chain()`
   - Valida se a cadeia foi criada com sucesso

2. **Validação**:
   - Se a cadeia não for criada, exibe mensagens de erro e possíveis soluções
   - Retorna caso a inicialização falhe

3. **Loop de Chat**:
   - Solicita entrada do usuário
   - Processa comandos especiais
   - Valida entrada vazia
   - Processa perguntas usando a cadeia RAG
   - Exibe respostas formatadas

4. **Tratamento de Erros**:
   - Captura `KeyboardInterrupt` (Ctrl+C)
   - Captura exceções genéricas
   - Loga erros e exibe mensagens amigáveis

**Comandos Especiais**:

| Comando | Ação |
|---------|------|
| `sair`, `quit`, `exit` | Encerra o chat |
| `ajuda`, `help` | Exibe mensagem de ajuda |
| `limpar`, `clear` | Limpa a tela e reexibe o banner |

**Exemplo de interação**:
```
PERGUNTA: Qual o faturamento da empresa?
Processando sua pergunta...

RESPOSTA: O faturamento foi de 10 milhões de reais.
------------------------------------------------------------
```

## Execução

### Execução direta

```bash
python src/chat.py
```

### Execução como módulo

```python
import sys
sys.path.append('src')
from chat import main

main()
```

## Fluxo de Execução Completo

```
┌─────────────────────┐
│   Início do Script  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  print_banner()     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Inicializar RAG    │
│  create_rag_chain() │
└──────────┬──────────┘
           │
           ├─► Sucesso
           │
           │   Falha
           ▼
┌─────────────────────┐
│  Exibir Erro        │
│  e Sugestões        │
│  └─► Sair           │
└─────────────────────┘

           │
           ▼
┌─────────────────────┐
│  Loop de Chat       │
│  ┌───────────────┐ │
│  │ Ler entrada   │ │
│  ├───────────────┤ │
│  │ Processar     │ │
│  │ comandos      │ │
│  ├───────────────┤ │
│  │ Validar       │ │
│  ├───────────────┤ │
│  │ Processar     │ │
│  │ pergunta      │ │
│  ├───────────────┤ │
│  │ Exibir        │ │
│  │ resposta      │ │
│  └───────────────┘ │
│         │           │
│         └─► Loop    │
└─────────────────────┘
```

## Tratamento de Erros

### 1. Falha na Inicialização

Se a cadeia RAG não for criada, o script exibe:

```
ERRO: Não foi possível iniciar o chat. Verifique os erros de inicialização.

POSSÍVEIS SOLUÇÕES:
1. Verifique se o banco de dados PostgreSQL está rodando
2. Execute primeiro: python src/ingest.py
3. Verifique as variáveis de ambiente no arquivo .env
4. Verifique se as API keys estão configuradas corretamente
```

### 2. Entrada Vazia

Se o usuário pressionar Enter sem digitar nada:

```
AVISO: Por favor, digite uma pergunta.
```

### 3. Erro ao Processar Pergunta

Se ocorrer um erro durante o processamento:

```
ERRO: Erro ao processar sua pergunta: [mensagem de erro]
Tente novamente ou digite 'ajuda' para ver os comandos disponíveis.
------------------------------------------------------------
```

O erro também é logado com `logger.error()` para debug.

### 4. Interrupção pelo Usuário (Ctrl+C)

Se o usuário pressionar Ctrl+C:

```
Chat interrompido pelo usuário. Até logo!
```

## Exemplo de Sessão Completa

```
============================================================
SISTEMA DE BUSCA SEMÂNTICA COM LANGCHAIN
============================================================
Digite 'sair' ou 'quit' para encerrar o chat
Digite 'ajuda' para ver comandos disponíveis
============================================================
Inicializando sistema de busca...
Sistema inicializado com sucesso!
Faça sua pergunta:
------------------------------------------------------------

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
Processando sua pergunta...

RESPOSTA: O faturamento foi de 10 milhões de reais.
------------------------------------------------------------

PERGUNTA: Qual o ano de fundação?
Processando sua pergunta...

RESPOSTA: A empresa foi fundada em 2020.
------------------------------------------------------------

PERGUNTA: Qual é a capital da França?
Processando sua pergunta...

RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
------------------------------------------------------------

PERGUNTA: ajuda

COMANDOS DISPONÍVEIS:
• Digite sua pergunta normalmente
• 'sair' ou 'quit' - Encerra o chat
• 'ajuda' - Mostra esta mensagem
• 'limpar' ou 'clear' - Limpa a tela
...

PERGUNTA: sair

Até logo! Chat encerrado.
```

## Mensagens do Sistema

### Banner Inicial
```
============================================================
SISTEMA DE BUSCA SEMÂNTICA COM LANGCHAIN
============================================================
Digite 'sair' ou 'quit' para encerrar o chat
Digite 'ajuda' para ver comandos disponíveis
============================================================
```

### Mensagens de Status
- `"Inicializando sistema de busca..."`
- `"Sistema inicializado com sucesso!"`
- `"Faça sua pergunta:"`
- `"Processando sua pergunta..."`

### Mensagens de Saída
- `"Até logo! Chat encerrado."`
- `"Chat interrompido pelo usuário. Até logo!"`

## Configuração de Logging

O script configura logging no nível `INFO`:

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

Os logs incluem:
- Erros durante a inicialização
- Erros durante o processamento de perguntas
- Informações de debug (se nível for alterado para `DEBUG`)

## Integração com Outros Scripts

Este script depende de:

- **`search.py`**: Importa `create_rag_chain()` para criar a cadeia RAG
- **`ingest.py`**: Deve ser executado antes para carregar os documentos no banco

**Fluxo recomendado**:
1. Execute `ingest.py` para carregar documentos
2. Execute `chat.py` para iniciar o chat interativo

## Considerações Importantes

1. **Dependência do Banco**: O script requer que a ingestão tenha sido executada previamente. Se a collection não existir, a inicialização falhará.

2. **Entrada de Usuário**: O script usa `input()` para leitura de entrada, que é bloqueante. O usuário deve digitar e pressionar Enter.

3. **Formatação de Resposta**: As respostas são exibidas com um formato consistente com separadores visuais.

4. **Case-Insensitive**: Os comandos especiais são verificados em lowercase, então funcionam independente de maiúsculas/minúsculas.

5. **Multiplataforma**: O script funciona em Windows, Linux e macOS, com tratamento adequado para limpeza de tela.

6. **Validação de Entrada**: O script valida entrada vazia antes de processar, evitando chamadas desnecessárias à cadeia RAG.

## Melhorias Futuras

Possíveis melhorias para o script:

1. **Histórico de Conversação**: Manter contexto entre perguntas
2. **Exportação de Conversas**: Salvar perguntas e respostas em arquivo
3. **Modo Batch**: Processar múltiplas perguntas de um arquivo
4. **Interface Web**: Criar uma interface web além da CLI
5. **Cores e Formatação**: Usar biblioteca `rich` para melhor formatação
6. **Autocomplete**: Sugestões ao digitar perguntas
7. **Streaming de Respostas**: Mostrar resposta conforme é gerada
8. **Métricas**: Mostrar tempo de processamento, número de documentos encontrados
9. **Feedback de Relevância**: Permitir que usuário avalie qualidade das respostas
10. **Múltiplos Documentos**: Permitir selecionar qual documento consultar
11. **Modo Verbose**: Mostrar documentos encontrados e scores de relevância
12. **Configuração**: Arquivo de configuração para personalizar comportamento

## Troubleshooting

### Problema: "Não foi possível iniciar o chat"

**Possíveis causas**:
- Banco de dados não está rodando
- Collection não existe (execute `ingest.py` primeiro)
- Variáveis de ambiente não configuradas
- API keys inválidas ou sem créditos

**Solução**: Siga as instruções exibidas na mensagem de erro.

### Problema: Respostas sempre retornam "Não tenho informações..."

**Possíveis causas**:
- Documentos não foram carregados corretamente
- Pergunta não está relacionada ao conteúdo
- Embeddings não foram gerados corretamente

**Solução**: 
- Verifique se a ingestão foi bem-sucedida
- Tente perguntas mais específicas
- Verifique os logs da ingestão

### Problema: Erro ao processar pergunta

**Possíveis causas**:
- Erro de conexão com banco
- Erro de API (sem créditos, rate limit, etc.)
- Erro interno do LLM

**Solução**: 
- Verifique os logs para detalhes
- Verifique se o banco está acessível
- Verifique se há créditos na API

