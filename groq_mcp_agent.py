
import logging
import regex 
import json
import os

from typing import Any, Dict, List
from dotenv import load_dotenv
from groq import Groq
from mcp import stdio_client
from mcp.client.session import ClientSession
from mcp_client import McpClient
from mcp_server import McpServer
from tool_info import ToolInfo

# Carrega variáveis de ambiente
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-groq-client")

class GroqMcpAgent:
    """Agent inteligente que usa Groq para orquestrar ferramentas MCP"""
    
    def __init__(self, groq_api_key: str = None):
        # Inicializa cliente Groq
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada")
        
        self.groq_client = Groq(api_key=api_key)
        self.servers: Dict[str, McpServer] = {}
        self.sessions: Dict[str, McpClient] = {}
        self.available_tools: Dict[str, ToolInfo] = {}
        
        # Histórico de conversação
        self.conversation_history = []
        
        # Configuração do Agent
        self.agent_model = "deepseek-r1-distill-llama-70b" #"mixtral-8x7b-32768"  # Melhor para raciocínio
        self.tool_model = "llama3-8b-8192"  # Mais rápido para execução

    def add_server(self, server: McpServer):
        """Adiciona um servidor MCP"""
        self.servers[server.name] = server
        logger.info(f"Servidor adicionado: {server.name}")

    async def connect_servers(self):
        if not self.servers:
            raise ValueError("Server not initialized or does not exist.")

        #self.sessions["filesystem"]
        async with stdio_client(self.servers.get("filesystem").params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                #  Initialize the connection
                await session.initialize()
                self.sessions["filesystem"] = session
                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    tool_key = f"{"filesystem"}:{tool.name}"
                    self.available_tools[tool_key] = ToolInfo(
                        name=tool.name,
                        description=tool.description,
                        input_schema=tool.inputSchema,
                        server_name="filesystem"
                    )

        #self.sessions["brave-search"]
        async with stdio_client(self.servers.get("brave-search").params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                #  Initialize the connection
                await session.initialize()
                self.sessions["brave-search"] = session
                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    tool_key = f"{"brave-search"}:{tool.name}"
                    self.available_tools[tool_key] = ToolInfo(
                        name=tool.name,
                        description=tool.description,
                        input_schema=tool.inputSchema,
                        server_name="brave-search"
                    )

    async def _initMCPFilesystem(self):
        """Conecta a todos os servidores MCP configurados"""
        # Define server parameters
        client = McpClient()
        server = self.servers.get("filesystem")

        await client.initialize_with_stdio(server.params)
        print(f"Server MCP: {server.name}")
        tools_result = await client.get_tools()
        for tool in tools_result:
            tool_key = f"{server.name}:{tool.name}"
            self.available_tools[tool_key] = ToolInfo(
                name=tool.name,
                description=tool.description,
                input_schema=tool.inputSchema,
                server_name=server.name
            )   

        return client

    async def _initMCPBrave(self):
        """Conecta a todos os servidores MCP configurados"""
        # Define server parameters
        client = McpClient()
        server = self.servers.get("brave-search")

        await client.initialize_with_stdio(server.params)
        print(f"Server MCP: {server.name}")
        tools_result = await client.get_tools()
        for tool in tools_result:
            tool_key = f"{server.name}:{tool.name}"
            self.available_tools[tool_key] = ToolInfo(
                name=tool.name,
                description=tool.description,
                input_schema=tool.inputSchema,
                server_name=server.name
            )   

        return client
    
    async def _initMCPClient(self, server_name: str):
        if server_name == "filesystem":
            return await self._initMCPFilesystem()
        if server_name == "brave-search":
            return await self._initMCPBrave()
        
        raise ValueError("The Server MCP does not exist.")

    def _prepare_tool_arguments(self, tool_info: ToolInfo, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara argumentos específicos para cada ferramenta"""
        schema_props = tool_info.input_schema.get('properties', {})
        
        # Filtra argumentos válidos
        valid_args = {}
        for key, value in params.items():
            if key in schema_props:
                valid_args[key] = value
        
        # Se não encontrou argumentos válidos, tenta mapear comuns
        if not valid_args and params:
            # Mapeia query/search/q para query se ferramenta aceita
            if 'query' in schema_props:
                for search_key in ['query', 'search', 'q', 'text']:
                    if search_key in params:
                        valid_args['query'] = params[search_key]
                        break
            
            # Mapeia path/file para path se ferramenta aceita        
            if 'path' in schema_props:
                for path_key in ['path', 'file', 'filename']:
                    if path_key in params:
                        valid_args['path'] = params[path_key]
                        break
        
        # Se ainda não tem argumentos, usa os originais (fallback)
        return valid_args if valid_args else params

    async def disconnect_servers(self):
        self.sessions.clear()

        logger.info("Cleanup de servidores concluído")

    def _build_tools_context(self) -> str:
        """Constrói contexto das ferramentas disponíveis para o Agent"""
        if not self.available_tools:
            return "Nenhuma ferramenta disponível."
        
        tools_desc = []
        for tool_key, tool in self.available_tools.items():
            server_name, tool_name = tool_key.split(":", 1)
            tools_desc.append(f"""
**{tool_key}**
- Descrição: {tool.description}
- Servidor: {server_name}
- Parâmetros: {json.dumps(tool.input_schema.get('properties', {}), indent=2)}
""")
        
        return "\n".join(tools_desc)

    async def _plan_execution(self, user_request: str) -> List[Dict[str, Any]]:
        """Usa Groq para planejar quais ferramentas usar"""
        tools_context = self._build_tools_context()
        
        system_prompt = f"""Você é um Agent inteligente que planeja a execução de tarefas usando ferramentas MCP disponíveis.

FERRAMENTAS DISPONÍVEIS:
{tools_context}

Sua tarefa é analisar a solicitação do usuário e criar um plano de execução usando as ferramentas disponíveis.

Regras:
- Se não souber como ajudar, retorne um plano vazio
- Use apenas ferramentas que existem
- Seja específico nos argumentos
- Considere dependências entre ferramentas

Super regra:
- Todo o processamento devera ser retornado como um JSON válido
- Sugestão:
{{
  "reasoning": "Explicação do seu raciocínio",
  "plan": [
    {{
      "tool": "servidor:ferramenta",
      "arguments": {{...}},
      "description": "O que esta etapa faz"
    }}
  ]
}}
"""

        try:
            completion = self.groq_client.chat.completions.create(
                model=self.agent_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Solicitação: {user_request}"}
                ],
                temperature=0.1,  # Baixa para ser mais determinístico
                max_tokens=2048,
            )
            
            response = completion.choices[0].message.content.strip()
            
            # Extrai JSON da resposta
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]

            match = regex.search(r'\{(?:[^{}]|(?R))*\}', response)

            if match:
                conteudo_com_chaves = match.group()
                # Remove as chaves externas
                response = f"{{{conteudo_com_chaves[1:-1]}}}"
                print(response)
            
            plan_data = json.loads(response)
            logger.info(f"Plano criado: {plan_data['reasoning']}")
            
            return plan_data.get("plan", [])
            
        except Exception as e:
            logger.error(f"Erro ao criar plano: {e}")
            return []

    async def _execute_tool(self, tool_key: str, params: Dict[str, Any]) -> str:
        """Executa uma ferramenta específica"""
        if tool_key not in self.available_tools:
            return f"Ferramenta {tool_key} não encontrada"
        
        tool_info = self.available_tools[tool_key]
        session = self.sessions.get(tool_info.server_name)
        
        if not session:
            return f"Sessão para servidor {tool_info.server_name} não encontrada"
        
        try:
            client = await self._initMCPClient(tool_info.server_name)
            arguments = self._prepare_tool_arguments(tool_info, params)

            result = await client.call_tool(tool_info.name, arguments)

            # Extrai conteúdo de texto dos resultados
            text_results = []
            for content in result.content:
                if hasattr(content, 'text'):
                    text_results.append(content.text)
                else:
                    text_results.append(str(content))
            
            return "\n".join(text_results)
            
        except Exception as e:
            logger.error(f"Erro ao executar {tool_key}: {e}")
            return f"Erro ao executar ferramenta: {str(e)}"
        finally:
            await client.cleanup()

    async def _synthesize_response(self, user_request: str, execution_results: List[Dict[str, Any]]) -> str:
        """Sintetiza uma resposta final usando os resultados"""
        results_context = []
        for result in execution_results:
            results_context.append(f"""
Ferramenta: {result['tool']}
Resultado: {result['result'][:500]}...
""")
        
        context = "\n".join(results_context)
        
        system_prompt = f"""Você é um assistente que sintetiza respostas baseado em resultados de ferramentas.

Solicitação original: {user_request}

Resultados das ferramentas executadas:
{context}

Crie uma resposta clara e útil para o usuário baseada nos resultados obtidos. 
Seja natural e conversacional, não mencione detalhes técnicos sobre as ferramentas."""

        try:
            completion = self.groq_client.chat.completions.create(
                model=self.tool_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Sintetize uma resposta baseada nos resultados acima."}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao sintetizar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

    async def process_request(self, user_request: str) -> str:
        """Processa uma solicitação completa do usuário"""
        logger.info(f"Processando: {user_request}")
        
        # Adiciona ao histórico
        self.conversation_history.append({"role": "user", "content": user_request})
        
        try:
            # 1. Planeja execução
            plan = await self._plan_execution(user_request)
            
            if not plan:
                response = "Desculpe, não sei como ajudar com essa solicitação com as ferramentas disponíveis."
                self.conversation_history.append({"role": "assistant", "content": response})
                return response
            
            # 2. Executa plano
            execution_results = []
            for step in plan:
                tool_key = step["tool"]
                arguments = step["arguments"]
                description = step.get("description", "")
                
                logger.info(f"Executando: {tool_key} - {description}")
                
                result = await self._execute_tool(tool_key, arguments)
                execution_results.append({
                    "tool": tool_key,
                    "description": description,
                    "result": result
                })
            
            # 3. Sintetiza resposta final
            final_response = await self._synthesize_response(user_request, execution_results)
            
            self.conversation_history.append({"role": "assistant", "content": final_response})
            
            return final_response
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            error_response = f"Erro ao processar solicitação: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_response})
            return error_response

    def get_available_tools(self) -> Dict[str, ToolInfo]:
        """Retorna ferramentas disponíveis"""
        return self.available_tools

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retorna histórico da conversação"""
        return self.conversation_history
