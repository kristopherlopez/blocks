from typing import Dict, Any, Callable, List, Optional, Union
import time
import uuid
import traceback
import re
import logging

# File: error_handling/error_handler.py

class ErrorType:
    """Error type classifications."""
    VALIDATION = "validation"
    EXECUTION = "execution"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    PERMISSION = "permission"
    AGENT = "agent"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class ErrorSeverity:
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Error:
    """Represents an error that occurred during workflow execution."""
    
    def __init__(self, message: str, error_type: str = ErrorType.UNKNOWN, original_error: Any = None):
        self.id = str(uuid.uuid4())
        self.message = message
        self.type = error_type
        self.original_error = original_error
        self.timestamp = time.time()
        self.severity = ErrorSeverity.MEDIUM
        self.source: Optional[str] = None
        self.node_id: Optional[str] = None
        self.workflow_id: Optional[str] = None
        self.execution_id: Optional[str] = None
        self.stacktrace: Optional[str] = None
        
        if original_error:
            self.stacktrace = traceback.format_exception(
                type(original_error), original_error, original_error.__traceback__)
    
    def set_severity(self, severity: str) -> None:
        """Set the error severity."""
        self.severity = severity
    
    def set_source(self, source: str) -> None:
        """Set the error source."""
        self.source = source
    
    def set_workflow_context(self, workflow_id: str, execution_id: str, node_id: Optional[str] = None) -> None:
        """Set the workflow context for the error."""
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.node_id = node_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            "id": self.id,
            "message": self.message,
            "type": self.type,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "source": self.source,
            "node_id": self.node_id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "stacktrace": self.stacktrace
        }

class Resolution:
    """Represents a resolution for an error."""
    
    def __init__(self, status: str, message: str):
        self.id = str(uuid.uuid4())
        self.status = status  # resolved, unresolved, retry, escalated
        self.message = message
        self.timestamp = time.time()
        self.actions: List[Dict[str, Any]] = []
    
    def add_action(self, action_type: str, **params) -> None:
        """Add an action to the resolution."""
        self.actions.append({
            "type": action_type,
            "params": params,
            "timestamp": time.time()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the resolution to a dictionary representation."""
        return {
            "id": self.id,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "actions": self.actions
        }

class RetryStrategy:
    """Defines a retry strategy for handling errors."""
    
    def __init__(self, max_attempts: int = 3, backoff: str = "exponential"):
        self.max_attempts = max_attempts
        self.backoff = backoff  # fixed, exponential, linear
        self.delay = 1.0  # Base delay in seconds
        self.max_delay = 60.0  # Maximum delay in seconds
        self.jitter = 0.1  # Random jitter factor
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate the delay for a retry attempt.
        
        Args:
            attempt: The current attempt number (1-based)
            
        Returns:
            The delay in seconds
        """
        import random
        
        if attempt <= 0:
            return 0
        
        if self.backoff == "fixed":
            delay = self.delay
        elif self.backoff == "linear":
            delay = self.delay * attempt
        else:  # exponential
            delay = self.delay * (2 ** (attempt - 1))
        
        # Apply jitter
        jitter_factor = 1.0 + random.uniform(-self.jitter, self.jitter)
        delay *= jitter_factor
        
        # Cap at max_delay
        return min(delay, self.max_delay)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the retry strategy to a dictionary representation."""
        return {
            "max_attempts": self.max_attempts,
            "backoff": self.backoff,
            "delay": self.delay,
            "max_delay": self.max_delay,
            "jitter": self.jitter
        }

class ErrorHandler:
    """
    Handles errors that occur during workflow execution.
    """
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.fallback_handler: Optional[Callable] = None
        self.global_error_node: Optional[str] = None
        self.retry_strategies: Dict[str, RetryStrategy] = {
            "transient_errors": RetryStrategy(3, "exponential"),
            "permanent_errors": RetryStrategy(1, "fixed")
        }
        self.error_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("error_handler")
    
    def register_handler(self, error_pattern: str, handler: Callable) -> None:
        """
        Register a handler for a specific error pattern.
        
        Args:
            error_pattern: A string pattern to match against error messages
            handler: A function that takes an Error object and context and returns a Resolution
        """
        if error_pattern not in self.handlers:
            self.handlers[error_pattern] = []
        
        self.handlers[error_pattern].append(handler)
    
    def set_fallback_handler(self, handler: Callable) -> None:
        """
        Set a fallback handler for errors that don't match any registered pattern.
        
        Args:
            handler: A function that takes an Error object and context and returns a Resolution
        """
        self.fallback_handler = handler
    
    def set_global_error_node(self, node_id: str) -> None:
        """Set the global error handler node ID."""
        self.global_error_node = node_id
    
    def configure_retry_strategy(self, error_type: str, max_attempts: int, backoff: str = "exponential",
                               delay: float = 1.0, max_delay: float = 60.0, jitter: float = 0.1) -> None:
        """Configure a retry strategy for a specific error type."""
        strategy = RetryStrategy(max_attempts, backoff)
        strategy.delay = delay
        strategy.max_delay = max_delay
        strategy.jitter = jitter
        self.retry_strategies[error_type] = strategy
    
    def should_retry(self, error: Error, attempt: int) -> bool:
        """
        Determine if an error should be retried.
        
        Args:
            error: The error to evaluate
            attempt: The current attempt number (1-based)
            
        Returns:
            Whether to retry the operation
        """
        # Get the appropriate retry strategy
        strategy = self.retry_strategies.get(error.type, self.retry_strategies["transient_errors"])
        
        # Check if we've reached the maximum attempts
        if attempt >= strategy.max_attempts:
            return False
        
        # For certain error types, never retry
        if error.type == ErrorType.PERMISSION or error.severity == ErrorSeverity.CRITICAL:
            return False
        
        return True
    
    def create_error(self, message: str, error_type: str = ErrorType.UNKNOWN, 
                    original_error: Any = None) -> Error:
        """Create a new Error object."""
        return Error(message, error_type, original_error)
    
    def create_resolution(self, status: str, message: str) -> Resolution:
        """Create a new Resolution object."""
        return Resolution(status, message)
    
    def handle_error(self, error: Union[Error, Any], context: Dict[str, Any] = None) -> Resolution:
        """
        Handle an error by finding and executing the appropriate handler.
        
        Args:
            error: The error to handle (Error object or exception)
            context: Optional context information for the error
            
        Returns:
            A Resolution object
        """
        # Convert to Error object if needed
        if not isinstance(error, Error):
            error = self.create_error(str(error), ErrorType.UNKNOWN, error)
        
        context = context or {}
        
        # Record error in history
        self.error_history.append(error.to_dict())
        
        # Log the error
        self.logger.error(f"Handling error: {error.message} (type: {error.type}, severity: {error.severity})")
        
        # Find matching handlers
        matching_handlers = []
        for pattern, handlers in self.handlers.items():
            if re.search(pattern, error.message):
                matching_handlers.extend(handlers)
        
        # Execute matching handlers
        if matching_handlers:
            for handler in matching_handlers:
                try:
                    result = handler(error, context)
                    if result:
                        if not isinstance(result, Resolution):
                            result = self.create_resolution(
                                result.get("status", "resolved"), 
                                result.get("message", "Error handled")
                            )
                        return result
                except Exception as e:
                    # If a handler fails, continue with the next one
                    self.logger.exception(f"Error in error handler: {e}")
                    continue
        
        # Use fallback handler if no matching handler or all handlers failed
        if self.fallback_handler:
            try:
                result = self.fallback_handler(error, context)
                if result:
                    if not isinstance(result, Resolution):
                        result = self.create_resolution(
                            result.get("status", "resolved"), 
                            result.get("message", "Error handled by fallback")
                        )
                    return result
            except Exception as e:
                self.logger.exception(f"Error in fallback handler: {e}")
        
        # Return a default resolution if all handlers fail
        return self.create_resolution("unhandled", f"Unhandled error: {error.message}")
    
    def get_error_history(self, workflow_id: Optional[str] = None, 
                         execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the error history, optionally filtered by workflow or execution.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            execution_id: Optional execution ID to filter by
            
        Returns:
            A list of error dictionaries
        """
        if not workflow_id and not execution_id:
            return self.error_history
        
        filtered_history = []
        for error in self.error_history:
            if workflow_id and error.get("workflow_id") != workflow_id:
                continue
            if execution_id and error.get("execution_id") != execution_id:
                continue
            filtered_history.append(error)
        
        return filtered_history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error handler configuration to a dictionary representation."""
        return {
            "global_error_node": self.global_error_node,
            "retry_strategies": {
                name: strategy.to_dict() 
                for name, strategy in self.retry_strategies.items()
            }
        }