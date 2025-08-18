
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class ToolInfo:
    """Informações de uma ferramenta MCP"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str