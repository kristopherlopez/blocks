"""
Tests for the WorkflowBuilder implementation.
"""

import pytest
from src.core.node import BaseNode
from src.core.workflow import WorkflowBuilder, Workflow

class TestWorkflowBuilder:
    """Test cases for WorkflowBuilder class."""
    
    def test_builder_creates_workflow(self):
        """Test that the builder creates a valid workflow."""
        # Arrange & Act
        builder = WorkflowBuilder("Test Workflow")
        workflow = builder.build()
        
        # Assert
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Test Workflow"
        assert workflow.id is not None  # Should have a generated UUID
    
    def test_builder_sets_properties(self):
        """Test that the builder sets all properties."""
        # Arrange
        builder = WorkflowBuilder("Test Workflow")
        builder.id("flow-1")
        builder.description("A test workflow")
        
        # Act
        workflow = builder.build()
        
        # Assert
        assert workflow.id == "flow-1"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
    
    def test_builder_adds_nodes(self):
        """Test that the builder adds nodes to the workflow."""
        # Arrange
        builder = WorkflowBuilder("Test Workflow")
        node1 = BaseNode("node1", "Node 1")
        node2 = BaseNode("node2", "Node 2")
        
        # Act
        builder.add_node(node1).add_node(node2)
        workflow = builder.build()
        
        # Assert
        assert len(workflow.nodes) == 2
        assert "node1" in workflow.nodes
        assert "node2" in workflow.nodes
    
    def test_builder_creates_connections(self):
        """Test that the builder creates connections between nodes."""
        # Arrange
        builder = WorkflowBuilder("Test Workflow")
        
        node1 = BaseNode("node1", "Node 1")
        node1.add_output_port("out1", "Output 1")
        
        node2 = BaseNode("node2", "Node 2")
        node2.add_input_port("in1", "Input 1")
        
        # Act
        builder.add_node(node1).add_node(node2)
        builder.connect("node1", "out1", "node2", "in1")
        workflow = builder.build()
        
        # Assert
        assert len(workflow.connections) == 1
        connection = workflow.connections[0]
        assert connection["source_node_id"] == "node1"
        assert connection["source_port_id"] == "out1"
        assert connection["target_node_id"] == "node2"
        assert connection["target_port_id"] == "in1"
    
    def test_building_a_simple_workflow(self):
        """Test building a complete simple workflow."""
        # Arrange
        class NumberNode(BaseNode):
            def __init__(self, id, value):
                super().__init__(id, f"Number {value}")
                self.value = value
                self.add_output_port("value", "Number Value")
            
            async def execute(self, inputs, context):
                return {"value": self.value}
        
        class AddNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Add Numbers")
                self.add_input_port("a", "First Number")
                self.add_input_port("b", "Second Number")
                self.add_output_port("sum", "Sum Result")
            
            async def execute(self, inputs, context):
                a = inputs.get("a", 0)
                b = inputs.get("b", 0)
                return {"sum": a + b}
        
        # Create nodes
        num5 = NumberNode("num5", 5)
        num7 = NumberNode("num7", 7)
        add = AddNode("add")
        
        # Act: Build the workflow
        workflow = (WorkflowBuilder("Math Workflow")
            .description("Simple addition workflow")
            .add_node(num5)
            .add_node(num7)
            .add_node(add)
            .connect("num5", "value", "add", "a")
            .connect("num7", "value", "add", "b")
            .build())
        
        # Assert
        assert workflow.name == "Math Workflow"
        assert "num5" in workflow.nodes
        assert "num7" in workflow.nodes
        assert "add" in workflow.nodes
        assert len(workflow.connections) == 2