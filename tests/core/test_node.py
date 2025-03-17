"""
Tests for the BaseNode implementation.
"""

import pytest
from src.core.node import BaseNode

class TestBaseNode:
    """Test cases for BaseNode class."""
    
    def test_node_initialization(self):
        """Test that a node can be created with basic properties."""
        # Arrange & Act
        node = BaseNode("test-1", "Test Node", "A test node")
        
        # Assert
        assert node.id == "test-1"
        assert node.name == "Test Node"
        assert node.description == "A test node"
        assert node.input_ports == {}
        assert node.output_ports == {}
    
    def test_add_input_port(self):
        """Test that input ports can be added to a node."""
        # Arrange
        node = BaseNode("test-1", "Test Node")
        
        # Act
        node.add_input_port("input-1", "First Input", "The first input port")
        
        # Assert
        assert "input-1" in node.input_ports
        assert node.input_ports["input-1"]["name"] == "First Input"
        assert node.input_ports["input-1"]["description"] == "The first input port"
    
    def test_add_output_port(self):
        """Test that output ports can be added to a node."""
        # Arrange
        node = BaseNode("test-1", "Test Node")
        
        # Act
        node.add_output_port("output-1", "First Output", "The first output port")
        
        # Assert
        assert "output-1" in node.output_ports
        assert node.output_ports["output-1"]["name"] == "First Output"
        assert node.output_ports["output-1"]["description"] == "The first output port"
    
    def test_method_chaining(self):
        """Test that port methods support chaining."""
        # Arrange
        node = BaseNode("test-1", "Test Node")
        
        # Act
        result = node.add_input_port("input-1", "Input").add_output_port("output-1", "Output")
        
        # Assert
        assert result is node
        assert "input-1" in node.input_ports
        assert "output-1" in node.output_ports
    
    async def test_execute_not_implemented(self):
        """Test that execute method raises NotImplementedError."""
        # Arrange
        node = BaseNode("test-1", "Test Node")
        
        # Act & Assert
        with pytest.raises(NotImplementedError):
            await node.execute({}, {})
    
    @pytest.mark.asyncio
    async def test_concrete_node_implementation(self):
        """Test a concrete implementation of BaseNode."""
        # Arrange
        class TestNode(BaseNode):
            """Simple test node implementation."""
            
            def __init__(self, id, name="Test Node"):
                super().__init__(id, name)
                self.add_input_port("value", "Input Value")
                self.add_output_port("result", "Output Result")
            
            async def execute(self, inputs, context):
                value = inputs.get("value", 0)
                return {"result": value * 2}
        
        node = TestNode("double", "Double Value")
        
        # Act
        result = await node.execute({"value": 5}, {})
        
        # Assert
        assert result["result"] == 10