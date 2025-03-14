from typing import Dict, Any, Callable, List, Optional

class ErrorHandler:
    """
    Handles errors that occur during workflow execution.
    """
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.fallback_handler: Optional[Callable] = None
    
    def register_handler(self, error_pattern: str, handler: Callable) -> None:
        """
        Register a handler for a specific error pattern.
        
        Args:
            error_pattern: A string pattern to match against error messages
            handler: A function that takes an error object and returns a resolution
        """
        if error_pattern not in self.handlers:
            self.handlers[error_pattern] = []
        
        self.handlers[error_pattern].append(handler)
    
    def set_fallback_handler(self, handler: Callable) -> None:
        """
        Set a fallback handler for errors that don't match any registered pattern.
        
        Args:
            handler: A function that takes an error object and returns a resolution
        """
        self.fallback_handler = handler
    
    def handle_error(self, error: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an error by finding and executing the appropriate handler.
        
        Args:
            error: The error to handle
            context: Optional context information for the error
            
        Returns:
            A dictionary with resolution information
        """
        error_message = str(error)
        context = context or {}
        
        # Find matching handlers
        matching_handlers = []
        for pattern, handlers in self.handlers.items():
            import re
            if re.search(pattern, error_message):
                matching_handlers.extend(handlers)
        
        # Execute matching handlers
        if matching_handlers:
            for handler in matching_handlers:
                try:
                    result = handler(error, context)
                    if result:
                        return result
                except Exception as e:
                    # If a handler fails, continue with the next one
                    import logging
                    logging.getLogger("error_handler").exception(
                        f"Error in error handler: {e}")
                    continue
        
        # Use fallback handler if no matching handler or all handlers failed
        if self.fallback_handler:
            try:
                return self.fallback_handler(error, context)
            except Exception as e:
                import logging
                logging.getLogger("error_handler").exception(
                    f"Error in fallback handler: {e}")
        
        # Return a default resolution if all handlers fail
        return {
            "status": "unhandled",
            "message": f"Unhandled error: {error_message}"
        }