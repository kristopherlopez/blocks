from typing import Dict, List, Any, Optional, Callable
import uuid

class Transition:
    """Represents a transition between static and dynamic sections of a workflow."""
    
    def __init__(self, transition_id: str, description: str = ""):
        self.id = transition_id or str(uuid.uuid4())
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transition to a dictionary representation."""
        return {
            "id": self.id,
            "description": self.description
        }

class StaticToDynamicTransition(Transition):
    """Represents a transition from a static workflow section to a dynamic section."""
    
    def __init__(self, transition_id: str, from_state: str, to_node: str, description: str = ""):
        super().__init__(transition_id, description)
        self.from_state = from_state
        self.to_node = to_node
        self.handover_data: List[str] = []
    
    def add_handover_data(self, variable: str) -> None:
        """Add a variable to be handed over from static to dynamic section."""
        if variable not in self.handover_data:
            self.handover_data.append(variable)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the static-to-dynamic transition to a dictionary representation."""
        result = super().to_dict()
        result.update({
            "from": self.from_state,
            "to": self.to_node,
            "handover_data": self.handover_data
        })
        return result

class DynamicToStaticTransition(Transition):
    """Represents a transition from a dynamic workflow section to a static section."""
    
    def __init__(self, transition_id: str, to_state: str, description: str = ""):
        super().__init__(transition_id, description)
        self.to_state = to_state
        self.trigger: Optional[str] = None
        self.required_data: List[str] = []
    
    def set_trigger(self, trigger: str) -> None:
        """Set the trigger expression for the transition."""
        self.trigger = trigger
    
    def add_required_data(self, variable: str) -> None:
        """Add a variable that is required for the transition."""
        if variable not in self.required_data:
            self.required_data.append(variable)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dynamic-to-static transition to a dictionary representation."""
        result = super().to_dict()
        result.update({
            "trigger": self.trigger,
            "to": self.to_state,
            "required_data": self.required_data
        })
        return result

class TransitionManager:
    """Manages transitions between static and dynamic sections of workflows."""
    
    def __init__(self):
        self.static_to_dynamic: Dict[str, StaticToDynamicTransition] = {}
        self.dynamic_to_static: Dict[str, DynamicToStaticTransition] = {}
        self.transition_handlers: Dict[str, Callable] = {}
    
    def add_static_to_dynamic(self, transition: StaticToDynamicTransition) -> None:
        """Add a static-to-dynamic transition."""
        self.static_to_dynamic[transition.id] = transition
    
    def add_dynamic_to_static(self, transition: DynamicToStaticTransition) -> None:
        """Add a dynamic-to-static transition."""
        self.dynamic_to_static[transition.id] = transition
    
    def register_handler(self, transition_id: str, handler: Callable) -> None:
        """Register a handler for a transition."""
        self.transition_handlers[transition_id] = handler
    
    def handle_static_to_dynamic(self, transition_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a transition from static to dynamic section.
        
        Args:
            transition_id: The ID of the transition
            context: The current workflow context
            
        Returns:
            The handover data for the dynamic section
        """
        if transition_id not in self.static_to_dynamic:
            raise ValueError(f"Transition {transition_id} does not exist")
        
        transition = self.static_to_dynamic[transition_id]
        
        # Extract handover data from context
        handover_data = {}
        for variable in transition.handover_data:
            if variable in context:
                handover_data[variable] = context[variable]
        
        # Execute custom handler if registered
        if transition_id in self.transition_handlers:
            handler = self.transition_handlers[transition_id]
            handler_result = handler(context, "static_to_dynamic", transition)
            if handler_result:
                handover_data.update(handler_result)
        
        return handover_data
    
    def handle_dynamic_to_static(self, transition_id: str, context: Dict[str, Any]) -> bool:
        """
        Handle a transition from dynamic to static section.
        
        Args:
            transition_id: The ID of the transition
            context: The current workflow context
            
        Returns:
            Whether the transition should be triggered
        """
        if transition_id not in self.dynamic_to_static:
            raise ValueError(f"Transition {transition_id} does not exist")
        
        transition = self.dynamic_to_static[transition_id]
        
        # Check if all required data is present
        for variable in transition.required_data:
            if variable not in context:
                return False
        
        # Evaluate trigger expression if present
        if transition.trigger:
            from engine.expression_evaluator import ExpressionEvaluator
            try:
                result = ExpressionEvaluator.evaluate(transition.trigger, context)
                if not result:
                    return False
            except Exception:
                return False
        
        # Execute custom handler if registered
        if transition_id in self.transition_handlers:
            handler = self.transition_handlers[transition_id]
            handler_result = handler(context, "dynamic_to_static", transition)
            if handler_result is False:  # Explicitly False, not falsy
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transition manager configuration to a dictionary representation."""
        return {
            "static_to_dynamic": {
                transition_id: transition.to_dict() 
                for transition_id, transition in self.static_to_dynamic.items()
            },
            "dynamic_to_static": {
                transition_id: transition.to_dict() 
                for transition_id, transition in self.dynamic_to_static.items()
            }
        }