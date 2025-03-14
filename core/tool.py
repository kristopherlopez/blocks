from typing import Dict, Optional, Any
import uuid

class Tool:
    """Represents a tool that agents can use during workflow execution."""
    
    def __init__(self, tool_id: str, name: str, description: str = "", 
                 tool_type: str = "function"):
        self.id = tool_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.type = tool_type  # api, function, resource, service
        self.input_schema: Optional[str] = None
        self.output_schema: Optional[str] = None
        self.config: Dict[str, Any] = {}
    
    def set_input_schema(self, schema_ref: str) -> None:
        """Set the input schema reference for the tool."""
        self.input_schema = schema_ref
    
    def set_output_schema(self, schema_ref: str) -> None:
        """Set the output schema reference for the tool."""
        self.output_schema = schema_ref
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the tool with the provided configuration."""
        self.config.update(config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "config": self.config
        }