from typing import Dict, Any

class ExpressionEvaluator:
    """
    Evaluates expressions used in workflow definitions.
    Expressions are enclosed in double curly braces: {{expression}}
    """
    
    @staticmethod
    def evaluate(expression: str, context: Dict[str, Any]) -> Any:
        """
        Evaluate an expression in the given context.
        
        Args:
            expression: The expression to evaluate
            context: The context containing variables
            
        Returns:
            The result of the expression evaluation
        """
        # Remove the double curly braces if present
        if expression.startswith("{{") and expression.endswith("}}"):
            expression = expression[2:-2].strip()
        
        # Create a safe evaluation environment
        # In a real implementation, this would use a proper expression parser
        # This is a simplified implementation for demonstration
        try:
            # Create a safe globals dict with only the functions we want to allow
            safe_globals = {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round
            }
            
            # Add the context to the locals
            # In a real implementation, this would handle nested references
            # using dot notation (e.g., context.customer.email)
            result = eval(expression, safe_globals, {"context": context})
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {expression}") from e
    
    @staticmethod
    def replace_expressions(template: str, context: Dict[str, Any]) -> str:
        """
        Replace all expressions in a template string with their evaluated values.
        
        Args:
            template: The template string containing expressions
            context: The context containing variables
            
        Returns:
            The template with expressions replaced by their values
        """
        import re
        
        # Find all expressions enclosed in double curly braces
        pattern = r"\{\{([^}]+)\}\}"
        
        def replace_match(match):
            expression = match.group(1).strip()
            try:
                result = ExpressionEvaluator.evaluate(expression, context)
                return str(result)
            except Exception as e:
                # Return the original expression if evaluation fails
                return f"{{{{{expression}}}}}"
        
        # Replace all expressions in the template
        result = re.sub(pattern, replace_match, template)
        return result