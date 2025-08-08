# 🤖 Groq Agent MCP

Um agente inteligente que utiliza o **Model Context Protocol (MCP)** para orquestrar ferramentas e serviços através da API do Groq. O agente é capaz de planejar e executar tarefas complexas usando múltiplos servidores MCP de forma autônoma.

## 🎯 Objetivo

Este projeto implementa um **agente inteligente** que:

- **Orquestra ferramentas MCP**: Conecta e gerencia múltiplos servidores MCP (filesystem, brave-search, etc.)
- **Planejamento inteligente**: Usa o Groq LLM para planejar quais ferramentas usar baseado no contexto
- **Execução autônoma**: Executa tarefas complexas sem intervenção manual
- **Síntese de respostas**: Combina resultados de múltiplas ferramentas em respostas coerentes

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  GroqMCPAgent   │───▶│  MCP Servers    │
│                 │    │                 │    │                 │
└─────────────────┘    │ • Planning      │    │ • Filesystem    │
                       │ • Execution     │    │ • Brave Search  │
                       │ • Synthesis     │    │ • (Extensible)  │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Groq API      │
                       │ (LLaMA3-8B)     │
                       └─────────────────┘
```

## ✨ Principais Funcionalidades

### 🧠 Agente Inteligente
- **Planejamento automático**: Analisa solicitações e cria planos de execução
- **Seleção de ferramentas**: Escolhe automaticamente as ferramentas MCP apropriadas
- **Execução sequencial**: Orquestra múltiplas ferramentas em sequência
- **Síntese de resultados**: Combina outputs de diferentes ferramentas

### 🔧 Ferramentas MCP Suportadas
- **Filesystem Server**: Leitura, escrita e manipulação de arquivos
- **Brave Search Server**: Busca na web e pesquisa de informações
- **Extensível**: Fácil adição de novos servidores MCP

### 💬 Interface Interativa
- **CLI interativo**: Interface de linha de comando amigável
- **Histórico de conversação**: Mantém contexto das interações
- **Feedback em tempo real**: Mostra progresso das operações

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Conta no Groq (API key)
- Conta no Brave Search (API key)

### 1. Clone o repositório
```bash
git clone <repository-url>
cd groq_agent_mcp
```

### 2. Configure o ambiente virtual
```bash
# Cria ambiente virtual
python -m venv venv

# Ativa o ambiente (macOS/Linux)
source venv/bin/activate

# Ativa o ambiente (Windows)
venv\Scripts\activate
```

### 3. Instale dependências Python
```bash
pip install -r requirements.txt
```

### 4. Instale servidores MCP
```bash
# Servidor de sistema de arquivos
npm install -g @modelcontextprotocol/server-filesystem

# Servidor de busca Brave
npm install -g @modelcontextprotocol/server-brave-search
```

### 5. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Chave da API do Groq (obtenha em: https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Chave da API Brave Search (obtenha em: https://api.search.brave.com/app/keys)
BRAVE_API_KEY=your_brave_api_key_here
```

## 🎮 Como Usar

### Execução Básica
```bash
python main.py
```

### Exemplos de Uso

#### 1. Busca e Análise de Informações
```
🔵 Você: Pesquise sobre inteligência artificial e salve os resultados em um arquivo
```

#### 2. Manipulação de Arquivos
```
🔵 Você: Liste os arquivos no diretório atual e crie um resumo
```

#### 3. Pesquisa Web
```
🔵 Você: Busque as últimas notícias sobre tecnologia e faça um resumo
```

## 📁 Estrutura do Projeto

```
groq_agent_mcp/
├── main.py              # Classe principal do agente e interface interativa
├── mcp_client.py        # Cliente MCP reutilizável
├── instructions.txt     # Instruções de setup e configuração
├── requirements.txt     # Dependências Python
├── README.md           # Este arquivo
├── .env               # Variáveis de ambiente (criar)
└── venv/              # Ambiente virtual Python
```

## 🔍 Componentes Principais

### `GroqMCPAgent`
- **Orquestração**: Gerencia múltiplos servidores MCP
- **Planejamento**: Usa Groq para criar planos de execução
- **Execução**: Executa ferramentas sequencialmente
- **Síntese**: Combina resultados em respostas coerentes

### `McpClient`
- **Cliente MCP**: Interface para comunicação com servidores
- **Gerenciamento de sessões**: Gerencia conexões com servidores
- **Chamadas de ferramentas**: Executa ferramentas MCP

### `InteractiveMCPClient`
- **Interface CLI**: Interface interativa para usuários
- **Configuração**: Setup automático de servidores padrão
- **Feedback**: Mostra progresso e resultados

## 🎯 Casos de Uso

### 1. **Pesquisa e Análise**
- Busca informações na web
- Analisa e sintetiza resultados
- Salva informações em arquivos

### 2. **Automação de Tarefas**
- Manipulação de arquivos
- Processamento de dados
- Geração de relatórios

### 3. **Assistente Inteligente**
- Resposta a perguntas complexas
- Execução de tarefas multi-step
- Síntese de informações

## 🔧 Configuração Avançada

### Adicionando Novos Servidores MCP

1. **Instale o servidor**:
```bash
npm install -g @modelcontextprotocol/server-example
```

2. **Configure no código**:
```python
# Em main.py, adicione ao método setup_default_servers()
self.agent.add_server(MCPServer(
    name="example",
    params=StdioServerParameters(
        command="npx",
        args=['-y', '@modelcontextprotocol/server-example'],
        env={'EXAMPLE_API_KEY': 'your_key'}
    )
))
```

### Personalizando Modelos

```python
# Em GroqMCPAgent.__init__()
self.agent_model = "llama3-8b-8192"  # Para planejamento
self.tool_model = "llama3-8b-8192"   # Para execução
```

## 🚀 Sugestões de Melhoria

### 1. **Funcionalidades**
- [ ] **Interface Web**: Dashboard web para visualização e controle
- [ ] **Persistência**: Salvar histórico de conversações em banco de dados
- [ ] **Plugins**: Sistema de plugins para extensibilidade
- [ ] **Multi-tenant**: Suporte a múltiplos usuários
- [ ] **Streaming**: Respostas em tempo real via WebSocket

### 2. **Integrações**
- [ ] **Slack/Discord**: Bot para plataformas de chat
- [ ] **API REST**: Endpoints para integração externa
- [ ] **Webhooks**: Notificações de eventos
- [ ] **Scheduler**: Execução de tarefas agendadas

### 3. **Melhorias Técnicas**
- [ ] **Cache**: Cache de resultados para melhor performance
- [ ] **Rate Limiting**: Controle de taxa de requisições
- [ ] **Error Handling**: Tratamento robusto de erros
- [ ] **Logging**: Sistema de logs estruturado
- [ ] **Monitoring**: Métricas e monitoramento

### 4. **Segurança**
- [ ] **Autenticação**: Sistema de autenticação
- [ ] **Autorização**: Controle de acesso por usuário
- [ ] **Audit Log**: Log de auditoria de ações
- [ ] **Encryption**: Criptografia de dados sensíveis

### 5. **Experiência do Usuário**
- [ ] **Templates**: Templates para tarefas comuns
- [ ] **Workflows**: Criação de workflows visuais
- [ ] **Documentation**: Documentação interativa
- [ ] **Tutorials**: Tutoriais guiados

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   ```
   ValueError: GROQ_API_KEY não encontrada
   ```
   - Verifique se o arquivo `.env` existe
   - Confirme se a chave está correta

2. **Servidor MCP não encontrado**
   ```
   ValueError: Server not initialized or does not exist
   ```
   - Instale os servidores MCP via npm
   - Verifique se os comandos estão corretos

3. **Erro de conexão**
   ```
   ConnectionError: Failed to connect
   ```
   - Verifique se os servidores estão rodando
   - Confirme as configurações de rede

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentação**: [Wiki](https://github.com/your-repo/wiki)
- **Email**: seu-email@exemplo.com

---

**Desenvolvido com ❤️ usando Groq e MCP**
