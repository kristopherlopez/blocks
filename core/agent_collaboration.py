from typing import Dict, List, Any, Optional, Callable
import uuid

class CollaborationPattern:
    """Defines a collaboration pattern between multiple agents."""
    
    def __init__(self, pattern_id: str, pattern_type: str, description: str = ""):
        self.id = pattern_id or str(uuid.uuid4())
        self.type = pattern_type  # sequential, parallel, hierarchical, debate
        self.description = description
        self.participants: List[str] = []
        self.coordinator: Optional[str] = None
        self.config: Dict[str, Any] = {}
    
    def add_participant(self, agent_id: str) -> None:
        """Add a participant agent to the collaboration."""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
    
    def set_coordinator(self, agent_id: str) -> None:
        """Set the coordinator agent for the collaboration."""
        self.coordinator = agent_id
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value for the collaboration."""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the collaboration pattern to a dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "participants": self.participants,
            "coordinator": self.coordinator,
            "config": self.config
        }

class MetaPlanningConfig:
    """Configuration for meta-planning capabilities."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.coordinator: Optional[str] = None
        self.strategy = "consensus"  # consensus, hierarchical, specialized
        self.evaluation_criteria: List[str] = []
        self.optimization_goal: Optional[str] = None
    
    def set_coordinator(self, agent_id: str) -> None:
        """Set the coordinator agent for meta-planning."""
        self.coordinator = agent_id
    
    def set_strategy(self, strategy: str) -> None:
        """Set the meta-planning strategy."""
        self.strategy = strategy
    
    def add_evaluation_criterion(self, criterion: str) -> None:
        """Add an evaluation criterion for plan evaluation."""
        if criterion not in self.evaluation_criteria:
            self.evaluation_criteria.append(criterion)
    
    def set_optimization_goal(self, goal: str) -> None:
        """Set the optimization goal for meta-planning."""
        self.optimization_goal = goal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the meta-planning configuration to a dictionary representation."""
        return {
            "enabled": self.enabled,
            "coordinator": self.coordinator,
            "strategy": self.strategy,
            "evaluation_criteria": self.evaluation_criteria,
            "optimization_goal": self.optimization_goal
        }

class CollaborationManager:
    """Manages agent collaboration and meta-planning."""
    
    def __init__(self):
        self.patterns: Dict[str, CollaborationPattern] = {}
        self.meta_planning = MetaPlanningConfig()
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
    
    def add_pattern(self, pattern: CollaborationPattern) -> None:
        """Add a collaboration pattern."""
        self.patterns[pattern.id] = pattern
    
    def configure_meta_planning(self, enabled: bool = True, strategy: str = "consensus",
                               coordinator: Optional[str] = None) -> None:
        """Configure meta-planning capabilities."""
        self.meta_planning.enabled = enabled
        self.meta_planning.strategy = strategy
        if coordinator:
            self.meta_planning.set_coordinator(coordinator)
    
    def start_collaboration(self, pattern_id: str, context: Dict[str, Any]) -> str:
        """
        Start a collaboration between agents.
        
        Args:
            pattern_id: The ID of the collaboration pattern to use
            context: The context for the collaboration
            
        Returns:
            A collaboration instance ID
        """
        if pattern_id not in self.patterns:
            raise ValueError(f"Collaboration pattern {pattern_id} does not exist")
        
        pattern = self.patterns[pattern_id]
        collaboration_id = str(uuid.uuid4())
        
        # In a real implementation, this would:
        # 1. Set up the collaboration between agents
        # 2. Start the collaboration process based on the pattern type
        # 3. Track the collaboration state
        
        self.active_collaborations[collaboration_id] = {
            "pattern_id": pattern_id,
            "status": "started",
            "context": context,
            "results": {}
        }
        
        return collaboration_id
    
    def get_collaboration_status(self, collaboration_id: str) -> Dict[str, Any]:
        """Get the status of a collaboration."""
        if collaboration_id not in self.active_collaborations:
            raise ValueError(f"Collaboration {collaboration_id} does not exist")
        
        return self.active_collaborations[collaboration_id]
    
    def end_collaboration(self, collaboration_id: str) -> Dict[str, Any]:
        """End a collaboration and return the results."""
        if collaboration_id not in self.active_collaborations:
            raise ValueError(f"Collaboration {collaboration_id} does not exist")
        
        collaboration = self.active_collaborations[collaboration_id]
        collaboration["status"] = "completed"
        
        return collaboration