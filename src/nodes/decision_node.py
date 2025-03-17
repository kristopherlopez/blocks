from src.core.node import BaseNode

class DecisionNode(BaseNode):
    """
    A node that makes a decision based on its input and routes accordingly.
    """
    
    def __init__(self, id, name, description=None):
        super().__init__(id, name, description or "Makes a decision based on input")
        self.add_input_port("input", "Decision Input")
        self.add_output_port("result", "Decision Result")
        self.add_output_port("input", "Pass-through of input data")
    
    async def execute(self, inputs, context):
        """
        Evaluate input and make a decision.
        
        The decision logic should be implemented by subclasses.
        """
        # Get input value
        input_value = inputs.get("input") or context.get_variable("input_data", "")
        
        # Evaluate (should be overridden by subclasses)
        result = await self._evaluate(input_value, context)
        
        # Return both the decision result and the original input
        return {
            "result": result,
            "input": input_value
        }
    
    async def _evaluate(self, input_value, context):
        """
        Evaluate the input and return a decision.
        
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Decision nodes must implement _evaluate method")