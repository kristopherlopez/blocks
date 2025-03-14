from typing import Dict, List, Any, Optional, Set
import copy
import json
import uuid

class ContextSnapshot:
    """Represents a snapshot of workflow context at a point in time."""
    
    def __init__(self, context: Dict[str, Any], timestamp: float, label: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.context = copy.deepcopy(context)
        self.timestamp = timestamp
        self.label = label
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the snapshot to a dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "label": self.label,
            "context": self.context
        }

class ContextScope:
    """Defines a scope for context variables."""
    
    def __init__(self, scope_id: str, parent_scope: Optional[str] = None):
        self.id = scope_id
        self.parent_scope = parent_scope
        self.variables: Dict[str, Any] = {}
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable in this scope."""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable from this scope."""
        return self.variables.get(name, default)
    
    def has_variable(self, name: str) -> bool:
        """Check if a variable exists in this scope."""
        return name in self.variables
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the scope to a dictionary representation."""
        return {
            "id": self.id,
            "parent_scope": self.parent_scope,
            "variables": self.variables
        }

class ContextManager:
    """
    Manages context for workflow execution, including variable scope,
    persistence, and isolation.
    """
    
    def __init__(self):
        self.scopes: Dict[str, ContextScope] = {}
        self.snapshots: List[ContextSnapshot] = []
        self.persistence_level = "workflow"  # workflow, subflow, both
        self.persistence_scope = ["variables"]  # variables, execution_history, agent_memory
        self.isolation_enabled = False
        self.isolation_exceptions: Set[str] = set()
    
    def create_scope(self, scope_id: str, parent_scope: Optional[str] = None) -> ContextScope:
        """Create a new context scope."""
        if scope_id in self.scopes:
            raise ValueError(f"Scope {scope_id} already exists")
        
        if parent_scope and parent_scope not in self.scopes:
            raise ValueError(f"Parent scope {parent_scope} does not exist")
        
        scope = ContextScope(scope_id, parent_scope)
        self.scopes[scope_id] = scope
        return scope
    
    def get_scope(self, scope_id: str) -> ContextScope:
        """Get a context scope by ID."""
        if scope_id not in self.scopes:
            raise ValueError(f"Scope {scope_id} does not exist")
        return self.scopes[scope_id]
    
    def set_variable(self, scope_id: str, name: str, value: Any) -> None:
        """Set a variable in a specific scope."""
        scope = self.get_scope(scope_id)
        scope.set_variable(name, value)
    
    def get_variable(self, scope_id: str, name: str, check_parents: bool = True, default: Any = None) -> Any:
        """
        Get a variable from a specific scope.
        
        Args:
            scope_id: The scope to check
            name: The variable name
            check_parents: Whether to check parent scopes if not found
            default: Default value if not found
            
        Returns:
            The variable value or default
        """
        scope = self.get_scope(scope_id)
        
        # Check in current scope
        if scope.has_variable(name):
            return scope.get_variable(name)
        
        # Check in parent scopes if requested
        if check_parents and scope.parent_scope:
            return self.get_variable(scope.parent_scope, name, True, default)
        
        return default
    
    def create_snapshot(self, scope_id: str, label: Optional[str] = None) -> str:
        """
        Create a snapshot of the current context.
        
        Args:
            scope_id: The scope to snapshot
            label: Optional label for the snapshot
            
        Returns:
            The snapshot ID
        """
        import time
        scope = self.get_scope(scope_id)
        
        # Create a merged context from this scope and its parents
        merged_context = {}
        current_scope_id = scope_id
        
        while current_scope_id:
            current_scope = self.get_scope(current_scope_id)
            # Add variables, not overriding those already added from child scopes
            for name, value in current_scope.variables.items():
                if name not in merged_context:
                    merged_context[name] = value
            
            current_scope_id = current_scope.parent_scope
        
        snapshot = ContextSnapshot(merged_context, time.time(), label)
        self.snapshots.append(snapshot)
        
        return snapshot.id
    
    def get_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Get a snapshot by ID."""
        for snapshot in self.snapshots:
            if snapshot.id == snapshot_id:
                return snapshot.to_dict()
        
        raise ValueError(f"Snapshot {snapshot_id} does not exist")
    
    def restore_snapshot(self, snapshot_id: str, scope_id: str) -> None:
        """
        Restore a snapshot to a specific scope.
        
        Args:
            snapshot_id: The snapshot to restore
            scope_id: The scope to restore to
        """
        snapshot_dict = None
        for snapshot in self.snapshots:
            if snapshot.id == snapshot_id:
                snapshot_dict = snapshot.context
                break
        
        if not snapshot_dict:
            raise ValueError(f"Snapshot {snapshot_id} does not exist")
        
        scope = self.get_scope(scope_id)
        
        # Clear existing variables and restore from snapshot
        scope.variables.clear()
        for name, value in snapshot_dict.items():
            scope.set_variable(name, value)
    
    def configure_persistence(self, level: str = "workflow", scope: List[str] = None) -> None:
        """Configure context persistence."""
        self.persistence_level = level
        if scope:
            self.persistence_scope = scope
    
    def configure_isolation(self, enabled: bool = True, exceptions: List[str] = None) -> None:
        """Configure context isolation."""
        self.isolation_enabled = enabled
        if exceptions:
            self.isolation_exceptions = set(exceptions)
    
    def persist_context(self, scope_id: str, storage_path: Optional[str] = None) -> None:
        """
        Persist context to storage.
        
        Args:
            scope_id: The scope to persist
            storage_path: Optional path to save to
        """
        # In a real implementation, this would persist to a file, database, etc.
        # This is a simplified implementation for demonstration
        
        # Get the context to persist based on persistence_level
        contexts_to_persist = {}
        
        if self.persistence_level == "workflow" or self.persistence_level == "both":
            # Find the root scope
            root_scope_id = scope_id
            current_scope = self.get_scope(scope_id)
            
            while current_scope.parent_scope:
                root_scope_id = current_scope.parent_scope
                current_scope = self.get_scope(root_scope_id)
            
            contexts_to_persist["workflow"] = self.get_scope(root_scope_id).to_dict()
        
        if self.persistence_level == "subflow" or self.persistence_level == "both":
            contexts_to_persist["subflow"] = self.get_scope(scope_id).to_dict()
        
        # In a real implementation, this would save to the storage_path
        if storage_path:
            with open(storage_path, 'w') as f:
                json.dump(contexts_to_persist, f)
    
    def load_context(self, scope_id: str, storage_path: str) -> None:
        """
        Load context from storage.
        
        Args:
            scope_id: The scope to load into
            storage_path: Path to load from
        """
        # In a real implementation, this would load from a file, database, etc.
        # This is a simplified implementation for demonstration
        
        try:
            with open(storage_path, 'r') as f:
                contexts = json.load(f)
            
            # Load based on persistence_level
            if self.persistence_level == "workflow" and "workflow" in contexts:
                # Find the root scope
                root_scope_id = scope_id
                current_scope = self.get_scope(scope_id)
                
                while current_scope.parent_scope:
                    root_scope_id = current_scope.parent_scope
                    current_scope = self.get_scope(root_scope_id)
                
                for name, value in contexts["workflow"]["variables"].items():
                    self.set_variable(root_scope_id, name, value)
            
            if self.persistence_level == "subflow" and "subflow" in contexts:
                for name, value in contexts["subflow"]["variables"].items():
                    self.set_variable(scope_id, name, value)
            
            if self.persistence_level == "both":
                if "workflow" in contexts:
                    # Find the root scope
                    root_scope_id = scope_id
                    current_scope = self.get_scope(scope_id)
                    
                    while current_scope.parent_scope:
                        root_scope_id = current_scope.parent_scope
                        current_scope = self.get_scope(root_scope_id)
                    
                    for name, value in contexts["workflow"]["variables"].items():
                        self.set_variable(root_scope_id, name, value)
                
                if "subflow" in contexts:
                    for name, value in contexts["subflow"]["variables"].items():
                        self.set_variable(scope_id, name, value)
        
        except Exception as e:
            raise ValueError(f"Error loading context: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the context manager configuration to a dictionary representation."""
        return {
            "persistence": {
                "level": self.persistence_level,
                "scope": self.persistence_scope
            },
            "isolation": {
                "enabled": self.isolation_enabled,
                "exceptions": list(self.isolation_exceptions)
            },
            "scopes": {scope_id: scope.to_dict() for scope_id, scope in self.scopes.items()},
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots]
        }