
from dataclasses import dataclass
from mcp import StdioServerParameters

@dataclass
class McpServer:
    """Configuração de um servidor MCP"""
    name: str
    params: StdioServerParameters
