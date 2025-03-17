"""
Tests for the workflow executor.
"""

import pytest
from src.core.node import BaseNode
from src.core.workflow import WorkflowBuilder
from src.core.executor import WorkflowExecutor

class TestWorkflowExecutor:
    """Test cases for WorkflowExecutor class."""
    
    @pytest.mark.asyncio
    async def test_execute_empty_workflow(self):
        """Test executing an empty workflow."""
        # Arrange
        workflow = WorkflowBuilder("Empty Workflow").build()
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert result["results"] == {}
    
    @pytest.mark.asyncio
    async def test_execute_single_node_workflow(self):
        """Test executing a workflow with a single node."""
        # Arrange
        class ConstantNode(BaseNode):
            def __init__(self, id, value):
                super().__init__(id, f"Constant {value}")
                self.value = value
                self.add_output_port("value", "Constant Value")
            
            async def execute(self, inputs, context):
                return {"value": self.value}
        
        node = ConstantNode("const", 42)
        workflow = WorkflowBuilder("Single Node").add_node(node).build()
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert "const" in result["results"]
        assert result["results"]["const"]["value"] == 42
    
    @pytest.mark.asyncio
    async def test_execute_linear_workflow(self):
        """Test executing a linear workflow with multiple nodes."""
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
        
        # Create workflow
        num5 = NumberNode("num5", 5)
        num7 = NumberNode("num7", 7)
        add = AddNode("add")
        
        workflow = (WorkflowBuilder("Math Workflow")
            .add_node(num5)
            .add_node(num7)
            .add_node(add)
            .connect("num5", "value", "add", "a")
            .connect("num7", "value", "add", "b")
            .build())
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert "num5" in result["results"]
        assert "num7" in result["results"]
        assert "add" in result["results"]
        assert result["results"]["num5"]["value"] == 5
        assert result["results"]["num7"]["value"] == 7
        assert result["results"]["add"]["sum"] == 12
    
    @pytest.mark.asyncio
    async def test_execute_complex_workflow(self):
        """Test executing a more complex workflow with branching."""
        # Arrange
        class InputNode(BaseNode):
            def __init__(self, id, name):
                super().__init__(id, name)
                self.add_output_port("value", "Input Value")
            
            async def execute(self, inputs, context):
                # UPDATED: Get value from initial context using get_variable
                return {"value": context.get_variable("input_value", 0)}
        
        class DoubleNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Double Value")
                self.add_input_port("value", "Input Value")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                value = inputs.get("value", 0)
                return {"result": value * 2}
        
        class SquareNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Square Value")
                self.add_input_port("value", "Input Value")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                value = inputs.get("value", 0)
                return {"result": value * value}
        
        class OutputNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Output Values")
                self.add_input_port("doubled", "Doubled Value")
                self.add_input_port("squared", "Squared Value")
                self.add_output_port("summary", "Summary Value")
            
            async def execute(self, inputs, context):
                doubled = inputs.get("doubled", 0)
                squared = inputs.get("squared", 0)
                return {"summary": f"Doubled: {doubled}, Squared: {squared}"}
        
        # Create workflow
        input_node = InputNode("input", "Input Value")
        double_node = DoubleNode("double")
        square_node = SquareNode("square")
        output_node = OutputNode("output")
        
        workflow = (WorkflowBuilder("Complex Workflow")
            .add_node(input_node)
            .add_node(double_node)
            .add_node(square_node)
            .add_node(output_node)
            .connect("input", "value", "double", "value")
            .connect("input", "value", "square", "value")
            .connect("double", "result", "output", "doubled")
            .connect("square", "result", "output", "squared")
            .build())
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow, {"input_value": 5})
        
        # Assert
        assert result["status"] == "completed"
        assert "input" in result["results"]
        assert "double" in result["results"]
        assert "square" in result["results"]
        assert "output" in result["results"]
        assert result["results"]["double"]["result"] == 10
        assert result["results"]["square"]["result"] == 25
        assert result["results"]["output"]["summary"] == "Doubled: 10, Squared: 25"
    
    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test executing a workflow where a node raises an error."""
        # Arrange
        class ErrorNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Error Node")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                raise ValueError("Test error")
        
        node = ErrorNode("error")
        workflow = WorkflowBuilder("Error Workflow").add_node(node).build()
        
        executor = WorkflowExecutor()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Test error"):
            await executor.execute_workflow(workflow)

    @pytest.mark.asyncio
    async def test_execute_with_missing_required_input(self):
        """Test executing a workflow where a node is missing a required input."""
        # Arrange
        class ProcessNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Process Node")
                self.add_input_port("data", "Required Input Data")
                self.add_output_port("result", "Process Result")
            
            async def execute(self, inputs, context):
                # This should never be called because validation will fail first
                data = inputs["data"]
                return {"result": f"Processed: {data}"}
        
        class SourceNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Source Node")
                self.add_output_port("wrong_output", "Wrong Output Port")
            
            async def execute(self, inputs, context):
                return {"wrong_output": "test data"}
        
        # Create nodes
        source_node = SourceNode("source")
        process_node = ProcessNode("process")
        
        # Build workflow with an intentionally wrong connection
        # Connect source.wrong_output to process.wrong_input (which doesn't exist)
        # This way, process node will have an incoming connection but not for the required port
        workflow = (WorkflowBuilder("Missing Input Workflow")
            .add_node(source_node)
            .add_node(process_node)
            .build())
        
        # Now add a manual connection to an input that doesn't match the required "data" port
        workflow.connections.append({
            "source_node_id": "source",
            "source_port_id": "wrong_output",
            "target_node_id": "process",
            "target_port_id": "wrong_input"  # This port doesn't exist, but it connects the nodes
        })
        
        executor = WorkflowExecutor()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Required input data for node 'process'"):
            await executor.execute_workflow(workflow)

    @pytest.mark.asyncio
    async def test_validation_skips_optional_inputs(self):
        """Test that validation doesn't fail for missing optional inputs."""
        # Arrange
        class FlexibleNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Flexible Node")
                self.add_input_port("required_data", "Required Input Data")
                self.add_input_port("optional_data", "Optional Input Data", required=False)
                self.add_output_port("result", "Process Result")
            
            async def execute(self, inputs, context):
                required = inputs["required_data"]
                optional = inputs.get("optional_data", "default value")
                return {"result": f"Required: {required}, Optional: {optional}"}
        
        source_node = BaseNode("source", "Source Node")
        source_node.add_output_port("output", "Output Data")
        
        flexible_node = FlexibleNode("flexible")
        
        # Create a workflow with only the required input connected
        workflow = (WorkflowBuilder("Optional Input Workflow")
            .add_node(source_node)
            .add_node(flexible_node)
            .connect("source", "output", "flexible", "required_data")
            .build())
        
        # Should not raise an error during validation
        
        # Add test execution
        class SimpleSourceNode(BaseNode):
            async def execute(self, inputs, context):
                return {"output": "test data"}
        
        # Replace the base node with an executable version
        workflow.nodes["source"] = SimpleSourceNode("source", "Source Node")
        workflow.nodes["source"].add_output_port("output", "Output Data")
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert result["results"]["flexible"]["result"] == "Required: test data, Optional: default value"

    @pytest.mark.asyncio
    async def test_validation_with_conditional_inputs(self):
        """Test validation with inputs coming from conditional routes."""
        # Arrange
        class DecisionNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Decision Node")
                self.add_output_port("value", "Output Value")
                self.add_output_port("condition", "Condition Result")
            
            async def execute(self, inputs, context):
                # Always output True for testing
                return {"value": "test data", "condition": True}
        
        class TargetNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Target Node")
                self.add_input_port("input_data", "Input Data")
                self.add_output_port("result", "Result")
            
            async def execute(self, inputs, context):
                return {"result": f"Processed: {inputs['input_data']}"}
        
        # Create nodes
        decision = DecisionNode("decision")
        target = TargetNode("target")
        
        # Create workflow with conditional route
        workflow = (WorkflowBuilder("Conditional Workflow")
            .add_node(decision)
            .add_node(target)
            .add_conditional_route("decision", "condition", True, "target", "input_data", "value")
            .build())
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert "target" in result["results"]
        assert result["results"]["target"]["result"] == "Processed: test data"

    @pytest.mark.asyncio
    async def test_start_node_with_context_inputs(self):
        """Test that start nodes can receive inputs from the execution context."""
        # Arrange
        class StartNodeWithInput(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Start Node With Input")
                self.add_input_port("context_data", "Data from Context")
                self.add_output_port("result", "Process Result")
            
            async def execute(self, inputs, context):
                # UPDATED: Use data from inputs or context with get_variable
                data = inputs.get("context_data") or context.get_variable("initial_value", "default")
                return {"result": f"Processed: {data}"}
        
        # Create workflow with a start node that has inputs
        start_node = StartNodeWithInput("start")
        workflow = WorkflowBuilder("Context Input Workflow").add_node(start_node).build()
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow, {"initial_value": "test context data"})
        
        # Assert
        assert result["status"] == "completed"
        assert result["results"]["start"]["result"] == "Processed: test context data"

    @pytest.mark.asyncio
    async def test_context_variable_access_in_nodes(self):
        """Test that nodes can access and modify context variables."""
        # Arrange
        class ContextAccessNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Context Access Node")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                # Read existing variable
                greeting = context.get_variable("greeting", "Hello")
                
                # Set a new variable
                context.set_variable("counter", context.get_variable("counter", 0) + 1)
                
                return {"result": f"{greeting} World"}
        
        node = ContextAccessNode("context_node")
        workflow = WorkflowBuilder("Context Access Workflow").add_node(node).build()
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow, {"greeting": "Hola"})
        
        # Assert
        assert result["status"] == "completed"
        assert result["results"]["context_node"]["result"] == "Hola World"
        # In the real implementation, you'd want to verify context.variables contains "counter": 1
        # But since the result doesn't include that, we can't easily assert it here

    @pytest.mark.asyncio
    async def test_execution_events_are_recorded(self):
        """Test that workflow execution generates the expected events."""
        # Arrange
        class SimpleNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Simple Node")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                return {"result": "success"}
        
        node = SimpleNode("simple")
        workflow = WorkflowBuilder("Simple Workflow").add_node(node).build()
        
        executor = WorkflowExecutor()
        
        # Act
        result = await executor.execute_workflow(workflow)
        
        # Assert
        assert result["status"] == "completed"
        assert result["event_count"] > 0
        # In a real test, you might want to inspect the actual events, but 
        # since they're not returned in the result, we're just checking count

    @pytest.mark.asyncio
    async def test_node_error_recording(self):
        """Test that node execution errors are properly recorded in the context."""
        # Arrange
        class ErrorNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Error Node")
                self.add_output_port("result", "Result Value")
            
            async def execute(self, inputs, context):
                raise ValueError("Intentional test error")
        
        node = ErrorNode("error_node")
        workflow = WorkflowBuilder("Error Workflow").add_node(node).build()
        
        executor = WorkflowExecutor()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Intentional test error"):
            await executor.execute_workflow(workflow)
            
        # In a real test, you'd verify the error was recorded in context.node_errors
        # But since we can't access the context after the exception, this is harder to test

    @pytest.mark.asyncio
    async def test_full_workflow_execution_lifecycle(self):
        """Test the complete lifecycle of workflow execution with context events."""
        # This test would require access to the context after execution
        # You might need to modify your executor to return the full context
        # or add a way to capture or inspect the context for testing
        
        # Arrange
        class StartNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Start Node")
                self.add_output_port("output", "Output Value")
            
            async def execute(self, inputs, context):
                return {"output": "start"}
        
        class ProcessNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Process Node")
                self.add_input_port("input", "Input Value")
                self.add_output_port("output", "Output Value")
            
            async def execute(self, inputs, context):
                context.set_variable("processed", True)
                return {"output": inputs["input"] + "_processed"}
        
        class EndNode(BaseNode):
            def __init__(self, id):
                super().__init__(id, "End Node")
                self.add_input_port("input", "Input Value")
                self.add_output_port("result", "Final Result")
            
            async def execute(self, inputs, context):
                return {"result": inputs["input"] + "_end"}
        
        # Create workflow
        start = StartNode("start")
        process = ProcessNode("process")
        end = EndNode("end")
        
        workflow = (WorkflowBuilder("Lifecycle Workflow")
            .add_node(start)
            .add_node(process)
            .add_node(end)
            .connect("start", "output", "process", "input")
            .connect("process", "output", "end", "input")
            .build())
        
        # You'd need to modify your executor to expose the context
        # or provide a way to capture events for testing