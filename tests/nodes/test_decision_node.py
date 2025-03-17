"""
Tests for decision nodes and conditional workflows.
"""

import pytest
from src.core.node import BaseNode
from src.nodes.decision_node import DecisionNode
from src.core.workflow import WorkflowBuilder
from src.core.executor import WorkflowExecutor

class TestConditionalWorkflow:
    """Test cases for conditional workflow branching."""
    
    @pytest.mark.asyncio
    async def test_simple_condition(self):
        """Test a simple conditional branch."""
        # Arrange
        class YesNoNode(DecisionNode):
            def __init__(self, id):
                super().__init__(id, "Yes/No Decision")
                # Override to make input optional
                self.add_input_port("input", "Decision Input", required=False)
            
            async def _evaluate(self, input_value, context):
                # Use input or get from context
                value = input_value or context.get_variable("input_data", "")
                if isinstance(value, str) and "yes" in value.lower():
                    return True
                return False
        
        class YesHandler(BaseNode):
            def __init__(self, id):
                super().__init__(id, "Yes Handler")
                self.add_input_port("input", "Input Data")
                self.add_output_port("result", "Result")
            
            async def execute(self, inputs, context):
                return {"result": "Handled YES"}
        
        class NoHandler(BaseNode):
            def __init__(self, id):
                super().__init__(id, "No Handler")
                self.add_input_port("input", "Input Data")
                self.add_output_port("result", "Result")
            
            async def execute(self, inputs, context):
                return {"result": "Handled NO"}
        
        # Create workflow
        decision = YesNoNode("decision")
        yes_handler = YesHandler("yes_handler")
        no_handler = NoHandler("no_handler")
        
        workflow = (WorkflowBuilder("Conditional Test")
            .add_node(decision)
            .add_node(yes_handler)
            .add_node(no_handler)
            .add_conditional_route("decision", "result", True, "yes_handler", "input", "input")
            .add_conditional_route("decision", "result", False, "no_handler", "input", "input")
            .build())
        
        executor = WorkflowExecutor()
        
        # Act: Execute with "yes" input
        result_yes = await executor.execute_workflow(
            workflow, 
            {"input_data": "yes, please"}
        )
        
        # Act: Execute with "no" input
        result_no = await executor.execute_workflow(
            workflow, 
            {"input_data": "no, thanks"}
        )
        
        # Print results for debugging
        print("YES RESULT:", result_yes["results"])
        print("NO RESULT:", result_no["results"])
        
        # Assert: Yes path
        assert "decision" in result_yes["results"]
        assert "yes_handler" in result_yes["results"]
        assert "no_handler" not in result_yes["results"]
        assert result_yes["results"]["yes_handler"]["result"] == "Handled YES"
        
        # Assert: No path
        assert "decision" in result_no["results"]
        assert "no_handler" in result_no["results"]
        assert "yes_handler" not in result_no["results"]
        assert result_no["results"]["no_handler"]["result"] == "Handled NO"
    
    @pytest.mark.asyncio
    async def test_inventory_check_workflow(self):
        """Test a workflow similar to inventory check in the order process."""
        # Arrange
        class OrderInputNode(BaseNode):
            def __init__(self, id, name="Order Input"):
                super().__init__(id, name)
                self.add_output_port("order", "Order Data")
            
            async def execute(self, inputs, context):
                # Get order from initial data
                return {"order": context.get_variable("order", {})}
        
        class InventoryCheckNode(DecisionNode):
            def __init__(self, id, name="Inventory Check"):
                super().__init__(id, name, "Check if item is in stock")
                # Override ports for clarity and make input optional
                self.add_input_port("input", "Decision Input", required=False)
                self.add_output_port("in_stock", "In Stock Result")
                self.add_output_port("order", "Order Data")
            
            async def _evaluate(self, input_value, context):
                # Check if item is in stock (mock implementation)
                item_id = input_value.get("item_id", "")
                # Simple rule: items with "available" in ID are in stock
                return "available" in item_id.lower()
            
            async def execute(self, inputs, context):
                order = inputs.get("order", {})
                in_stock = await self._evaluate(order, context)
                return {
                    "in_stock": in_stock,
                    "order": order
                }
        
        class PackItemNode(BaseNode):
            def __init__(self, id, name="Pack Item"):
                super().__init__(id, name)
                self.add_input_port("order", "Order Data")
                self.add_output_port("result", "Pack Result")
            
            async def execute(self, inputs, context):
                order = inputs.get("order", {})
                return {"result": f"Packed item {order.get('item_id', 'unknown')}"}
        
        class CancelOrderNode(BaseNode):
            def __init__(self, id, name="Cancel Order"):
                super().__init__(id, name)
                self.add_input_port("order", "Order Data")
                self.add_output_port("result", "Cancel Result")
            
            async def execute(self, inputs, context):
                order = inputs.get("order", {})
                return {"result": f"Cancelled order for item {order.get('item_id', 'unknown')}"}
        
        # Create workflow
        order_input = OrderInputNode("order_input")
        inventory_check = InventoryCheckNode("inventory_check")
        pack_item = PackItemNode("pack_item")
        cancel_order = CancelOrderNode("cancel_order")
        
        workflow = (WorkflowBuilder("Inventory Workflow")
            .add_node(order_input)
            .add_node(inventory_check)
            .add_node(pack_item)
            .add_node(cancel_order)
            .connect("order_input", "order", "inventory_check", "order")
            .add_conditional_route("inventory_check", "in_stock", True, "pack_item", "order", "order")
            .add_conditional_route("inventory_check", "in_stock", False, "cancel_order", "order", "order")
            .build())
        
        executor = WorkflowExecutor()
        
        # Act: Item in stock
        result_in_stock = await executor.execute_workflow(
            workflow, 
            {"order": {"item_id": "item-available-1234", "quantity": 1}}
        )
        
        # Act: Item not in stock
        result_out_of_stock = await executor.execute_workflow(
            workflow, 
            {"order": {"item_id": "item-backordered-5678", "quantity": 1}}
        )
        
        # Print results for debugging
        print("IN STOCK RESULT:", result_in_stock["results"])
        print("OUT OF STOCK RESULT:", result_out_of_stock["results"])
        
        # Assert: In stock path
        assert "inventory_check" in result_in_stock["results"]
        assert result_in_stock["results"]["inventory_check"]["in_stock"] is True
        assert "pack_item" in result_in_stock["results"]
        assert "cancel_order" not in result_in_stock["results"]
        
        # Assert: Out of stock path
        assert "inventory_check" in result_out_of_stock["results"]
        assert result_out_of_stock["results"]["inventory_check"]["in_stock"] is False
        assert "cancel_order" in result_out_of_stock["results"]
        assert "pack_item" not in result_out_of_stock["results"]