"""
Tests for the Workflow implementation.
"""

import pytest
from src.core.node import BaseNode
from src.core.workflow import Workflow

class TestWorkflow:
    """Test cases for Workflow class."""
    
    def test_workflow_initialization(self):
        """Test that a workflow can be created with basic properties."""
        # Arrange & Act
        workflow = Workflow("flow-1", "Test Workflow", "A test workflow")
        
        # Assert
        assert workflow.id == "flow-1"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.nodes == {}
        assert workflow.connections == []
    
    def test_add_node(self):
        """Test that nodes can be added to a workflow."""
        # Arrange
        workflow = Workflow("flow-1", "Test Workflow")
        node = BaseNode("node-1", "Test Node")
        
        # Act
        result = workflow.add_node(node)
        
        # Assert
        assert result is workflow  # Method chaining
        assert "node-1" in workflow.nodes
        assert workflow.nodes["node-1"] is node
    
    def test_connect_nodes(self):
        """Test that nodes can be connected in a workflow."""
        # Arrange
        workflow = Workflow("flow-1", "Test Workflow")
        source_node = BaseNode("source", "Source Node")
        source_node.add_output_port("output", "Output")
        
        target_node = BaseNode("target", "Target Node")
        target_node.add_input_port("input", "Input")
        
        workflow.add_node(source_node)
        workflow.add_node(target_node)
        
        # Act
        result = workflow.connect("source", "output", "target", "input")
        
        # Assert
        assert result is workflow  # Method chaining
        assert len(workflow.connections) == 1
        
        connection = workflow.connections[0]
        assert connection["source_node_id"] == "source"
        assert connection["source_port_id"] == "output"
        assert connection["target_node_id"] == "target"
        assert connection["target_port_id"] == "input"
    
    def test_multiple_connections(self):
        """Test that multiple connections can be created."""
        # Arrange
        workflow = Workflow("flow-1", "Test Workflow")
        
        node1 = BaseNode("node1", "Node 1")
        node1.add_output_port("out1", "Output 1")
        
        node2 = BaseNode("node2", "Node 2")
        node2.add_input_port("in1", "Input 1")
        node2.add_output_port("out1", "Output 1")
        
        node3 = BaseNode("node3", "Node 3")
        node3.add_input_port("in1", "Input 1")
        
        workflow.add_node(node1).add_node(node2).add_node(node3)
        
        # Act
        workflow.connect("node1", "out1", "node2", "in1")
        workflow.connect("node2", "out1", "node3", "in1")
        
        # Assert
        assert len(workflow.connections) == 2
        assert workflow.connections[0]["source_node_id"] == "node1"
        assert workflow.connections[0]["target_node_id"] == "node2"
        assert workflow.connections[1]["source_node_id"] == "node2"
        assert workflow.connections[1]["target_node_id"] == "node3"