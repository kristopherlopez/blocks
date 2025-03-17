"""
Tests for the execution context.
"""

import pytest
import time
from src.core.context import ExecutionContext

class TestExecutionContext:
    """Test cases for ExecutionContext class."""
    
    def test_context_initialization(self):
        """Test basic context initialization."""
        # Arrange & Act
        context = ExecutionContext("workflow-1", "exec-1", {"initial": "value"})
        
        # Assert
        assert context.workflow_id == "workflow-1"
        assert context.execution_id == "exec-1"
        assert context.variables == {"initial": "value"}
        assert context.node_results == {}
        assert context.node_errors == {}
        assert len(context.completed_nodes) == 0
        assert len(context.pending_nodes) == 0
        assert len(context.execution_history) == 0
        assert context.status == "created"
        assert context.error is None
    
    def test_variable_management(self):
        """Test setting and getting variables."""
        # Arrange
        context = ExecutionContext("workflow-1", "exec-1")
        
        # Act
        context.set_variable("test_var", "test_value")
        
        # Assert
        assert context.get_variable("test_var") == "test_value"
        assert context.get_variable("non_existent") is None
        assert context.get_variable("non_existent", "default") == "default"
        
        # Verify event was recorded
        events = context.get_execution_history()
        assert len(events) == 1
        assert events[0]["type"] == "variable_set"
        assert events[0]["variable_name"] == "test_var"
    
    def test_node_result_management(self):
        """Test setting and getting node results."""
        # Arrange
        context = ExecutionContext("workflow-1", "exec-1")
        
        # Act
        context.set_node_result("node-1", {"port1": "value1", "port2": 42})
        
        # Assert
        assert context.get_node_result("node-1") == {"port1": "value1", "port2": 42}
        assert context.get_node_result("node-1", "port1") == "value1"
        assert context.get_node_result("node-1", "port2") == 42
        assert context.get_node_result("node-1", "non_existent") is None
        assert context.get_node_result("non_existent") == {}
    
    def test_node_state_management(self):
        """Test marking nodes as pending or complete."""
        # Arrange
        context = ExecutionContext("workflow-1", "exec-1")
        
        # Act & Assert - Mark pending
        context.mark_node_pending("node-1")
        assert "node-1" in context.pending_nodes
        assert "node-1" not in context.completed_nodes
        
        # Act & Assert - Mark complete
        context.mark_node_complete("node-1")
        assert "node-1" not in context.pending_nodes
        assert "node-1" in context.completed_nodes
    
    def test_execution_history(self):
        """Test recording and retrieving execution history."""
        # Arrange
        context = ExecutionContext("workflow-1", "exec-1")
        
        # Act
        context.add_execution_event({"type": "custom_event", "data": "test"})
        time.sleep(0.01)  # Ensure timestamps are different
        context.add_execution_event({"type": "another_event"})
        
        # Assert
        history = context.get_execution_history()
        assert len(history) == 2
        assert history[0]["type"] == "custom_event"
        assert history[0]["data"] == "test"
        assert history[1]["type"] == "another_event"
        assert "timestamp" in history[0]
        assert "timestamp" in history[1]
        assert history[0]["timestamp"] < history[1]["timestamp"]
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        # Arrange
        context = ExecutionContext("workflow-1", "exec-1", {"initial": "value"})
        context.set_node_result("node-1", {"output": "value"})
        context.set_node_error("node-2", "Error message")
        context.mark_node_complete("node-1")
        context.mark_node_pending("node-3")
        
        # Act
        result = context.to_dict()
        
        # Assert
        assert result["workflow_id"] == "workflow-1"
        assert result["execution_id"] == "exec-1"
        assert result["variables"] == {"initial": "value"}
        assert result["node_results"] == {"node-1": {"output": "value"}}
        assert result["node_errors"] == {"node-2": "Error message"}
        assert "node-1" in result["completed_nodes"]
        assert "node-3" in result["pending_nodes"]
        assert result["status"] == "created"