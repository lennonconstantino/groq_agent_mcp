#!/usr/bin/env python3
"""
MCP Client com Agent inteligente usando Groq
O Agent decide quais ferramentas MCP usar baseado no contexto
"""
import asyncio
import logging
import os

from dotenv import load_dotenv
from mcp import StdioServerParameters

from groq_mcp_agent import GroqMcpAgent
from mcp_server import McpServer

# Carrega variáveis de ambiente
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-groq-client")

class InteractiveMCPClient:
    """Interface interativa para o Agent MCP"""
    
    def __init__(self):
        self.agent = GroqMcpAgent()
        self.setup_default_servers()

    def setup_default_servers(self):
        """Configura servidores MCP padrão"""
        # Exemplo: servidor de sistema de arquivos
        self.agent.add_server(McpServer(
            name="filesystem",
            params=StdioServerParameters(
                command="npx",                                                   # The command to run your server
                args=['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],  # Arguments to the command
            )
        ))
        
        # Exemplo: servidor de busca web
        self.agent.add_server(McpServer(
            name="brave-search",
            params=StdioServerParameters(
                command="npx",                                             # The command to run your server
                args=['-y', '@modelcontextprotocol/server-brave-search'],  # Arguments to the command
                env={'BRAVE_API_KEY': os.getenv("BRAVE_API_KEY")}
            )
        ))

    async def start(self):
        """Inicia o cliente interativo"""
        print("🤖 MCP Client com Agent Groq")
        print("="*40)
        
        try:
            # Conecta aos servidores
            print("Conectando aos servidores MCP...")
            await self.agent.connect_servers()
            
            # Mostra ferramentas disponíveis
            tools = self.agent.get_available_tools()
            print(f"\n✅ {len(tools)} ferramentas disponíveis:")
            for tool_key, tool in tools.items():
                print(f"  • {tool_key}: {tool.description}")
            
            print()
            print("\n💬 Digite suas solicitações (ou 'quit' para sair):")
            print("-" * 40)
            print()
            
            # Loop interativo
            while True:
                try:
                    user_input = input("\n🔵 Você: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'sair']:
                        break
                    
                    if not user_input:
                        continue
                    
                    print("🔄 Processando...")
                    response = await self.agent.process_request(user_input)
                    print(f"🤖 Agent: {response}")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Erro: {e}")
            
        finally:
            print("\n👋 Desconectando...")
            await self.agent.disconnect_servers()
            #asyncio.run(self.agent.disconnect_servers())
            print("Finalizado!")

async def main():
    """Função principal"""
    try:
        client = InteractiveMCPClient()
        await client.start()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
