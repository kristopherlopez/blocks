from typing import Dict, Any, List, Optional
import yaml
from core.workflow import Workflow, WorkflowMetadata, WorkflowVersioning, ExecutionSettings, WorkflowVariable
from core.agent import Agent
from core.tool import Tool
from core.node import Node
from nodes.task_node import TaskNode
from nodes.decision_node import DecisionNode
from nodes.agent_node import AgentNode
from nodes.subflow_node import SubflowNode
from nodes.wait_node import WaitNode

class WorkflowParser:
    """
    Parses workflow definitions from YAML files and creates Workflow objects.
    """
    
    @staticmethod
    def parse_from_file(file_path: str) -> Workflow:
        """
        Parse a workflow definition from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            A Workflow object representing the parsed workflow
        """
        with open(file_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
        
        return WorkflowParser.parse_from_dict(yaml_content)
    
    @staticmethod
    def parse_from_string(yaml_string: str) -> Workflow:
        """
        Parse a workflow definition from a YAML string.
        
        Args:
            yaml_string: YAML string containing the workflow definition
            
        Returns:
            A Workflow object representing the parsed workflow
        """
        yaml_content = yaml.safe_load(yaml_string)
        return WorkflowParser.parse_from_dict(yaml_content)
    
    @staticmethod
    def parse_from_dict(yaml_content: Dict[str, Any]) -> Workflow:
        """
        Parse a workflow definition from a dictionary.
        
        Args:
            yaml_content: Dictionary containing the workflow definition
            
        Returns:
            A Workflow object representing the parsed workflow
        """
        # Extract the workflow section
        workflow_data = yaml_content.get("workflow", {})
        
        # Create the workflow
        name = workflow_data.get("name", "Unnamed Workflow")
        description = workflow_data.get("description", "")
        version = workflow_data.get("version", "0.1.0")
        
        workflow = Workflow(name, description, version)
        
        # Parse metadata
        if "metadata" in workflow_data:
            metadata = workflow_data["metadata"]
            workflow.metadata = WorkflowMetadata(
                owner=metadata.get("owner", ""),
                created_at=metadata.get("created_at"),
                tags=metadata.get("tags", []),
                flow_type=metadata.get("flow_type", "static")
            )
        
        # Parse versioning
        if "versioning" in workflow_data:
            versioning = workflow_data["versioning"]
            workflow.versioning = WorkflowVersioning(
                version=version,
                previous_version=versioning.get("previous_version"),
                migration_strategy=versioning.get("migration_strategy")
            )
        
        # Parse execution settings
        if "execution" in workflow_data:
            execution = workflow_data["execution"]
            workflow.execution = ExecutionSettings(
                mode=execution.get("mode", "static"),
                concurrency=execution.get("concurrency", 1),
                timeout=execution.get("timeout"),
                retry=execution.get("retry", {"max_attempts": 3, "backoff": "exponential"}),
                idempotency_key=execution.get("idempotency_key"),
                dynamic_sections=execution.get("dynamic_sections", []),
                static_sections=execution.get("static_sections", [])
            )
        
        # Parse variables
        if "variables" in workflow_data:
            for var_name, var_data in workflow_data["variables"].items():
                variable = WorkflowVariable(
                    name=var_name,
                    type_=var_data.get("type", "string"),
                    description=var_data.get("description", ""),
                    schema_ref=var_data.get("schema_ref"),
                    scope=var_data.get("scope", "workflow")
                )
                workflow.add_variable(variable)
        
        # Parse agents
        if "agents" in workflow_data:
            for agent_id, agent_data in workflow_data["agents"].items():
                agent = Agent(
                    agent_id=agent_id,
                    name=agent_data.get("name", agent_id),
                    role=agent_data.get("role", ""),
                    description=agent_data.get("description", "")
                )
                
                # Set agent capabilities
                for capability in agent_data.get("capabilities", []):
                    agent.add_capability(capability)
                
                # Set agent goal
                if "goal" in agent_data:
                    agent.set_goal(agent_data["goal"])
                
                # Set agent constraints
                for constraint in agent_data.get("constraints", []):
                    agent.add_constraint(constraint)
                
                # Set knowledge base
                if "knowledge_base" in agent_data:
                    agent.set_knowledge_base(agent_data["knowledge_base"])
                
                # Configure memory
                if "memory" in agent_data:
                    memory_data = agent_data["memory"]
                    agent.configure_memory(
                        memory_type=memory_data.get("type", "short_term"),
                        config=memory_data.get("config", {})
                    )
                
                # Add tools
                for tool in agent_data.get("tools", []):
                    agent.add_tool(
                        tool_id=tool.get("tool_id"),
                        permissions=tool.get("permissions", ["use"])
                    )
                
                # Configure workflow execution
                if "workflow_execution" in agent_data:
                    we_data = agent_data["workflow_execution"]
                    for workflow_id in we_data.get("can_execute", []):
                        agent.add_executable_workflow(workflow_id)
                    
                    for permission in we_data.get("permissions", []):
                        agent.add_execution_permission(permission)
                
                workflow.add_agent(agent)
        
        # Parse tools
        if "tools" in workflow_data:
            for tool_id, tool_data in workflow_data["tools"].items():
                tool = Tool(
                    tool_id=tool_id,
                    name=tool_data.get("name", tool_id),
                    description=tool_data.get("description", ""),
                    tool_type=tool_data.get("type", "function")
                )
                
                # Set schemas
                if "input_schema" in tool_data:
                    tool.set_input_schema(tool_data["input_schema"])
                
                if "output_schema" in tool_data:
                    tool.set_output_schema(tool_data["output_schema"])
                
                # Configure the tool
                if "config" in tool_data:
                    tool.configure(tool_data["config"])
                
                workflow.add_tool(tool)
        
        # Parse nodes
        if "nodes" in workflow_data:
            for node_id, node_data in workflow_data["nodes"].items():
                node_type = node_data.get("type", "task")
                description = node_data.get("description", "")
                
                # Create node based on type
                if node_type == "task":
                    node = TaskNode(node_id, description)
                    if "config" in node_data:
                        config = node_data["config"]
                        if "task_type" in config:
                            node.set_task_type(config["task_type"])
                        if "assign_to" in config:
                            node.set_assignee(config["assign_to"])
                        if "parameters" in config:
                            node.set_parameters(config["parameters"])
                
                elif node_type == "decision":
                    node = DecisionNode(node_id, description)
                    if "config" in node_data and "condition" in node_data["config"]:
                        node.set_condition(node_data["config"]["condition"])
                
                elif node_type == "agent":
                    agent_id = node_data.get("agent", "")
                    node = AgentNode(node_id, agent_id, description)
                    
                    if "config" in node_data:
                        config = node_data["config"]
                        if "goal" in config:
                            node.set_goal(config["goal"])
                        if "max_iterations" in config:
                            node.set_max_iterations(config["max_iterations"])
                        if "tools" in config:
                            for tool_id in config["tools"]:
                                node.add_tool(tool_id)
                        if "planning" in config:
                            planning = config["planning"]
                            node.configure_planning(
                                enabled=planning.get("enabled", True),
                                strategy=planning.get("strategy", "goal-based"),
                                plan_visibility=planning.get("plan_visibility", "observable")
                            )
                        if "delegation" in config:
                            delegation = config["delegation"]
                            node.configure_delegation(
                                can_delegate=delegation.get("can_delegate", False),
                                delegation_scope=delegation.get("delegation_scope", [])
                            )
                
                elif node_type == "subflow":
                    workflow_ref = node_data.get("workflow_ref", "")
                    node = SubflowNode(node_id, workflow_ref, description)
                    
                    # Map inputs and outputs
                    if "input_mapping" in node_data:
                        for parent_var, subflow_var in node_data["input_mapping"].items():
                            node.map_input(parent_var, subflow_var)
                    
                    if "output_mapping" in node_data:
                        for subflow_var, parent_var in node_data["output_mapping"].items():
                            node.map_output(subflow_var, parent_var)
                    
                    # Configure execution
                    if "execution" in node_data:
                        execution = node_data["execution"]
                        if "wait_for_completion" in execution:
                            node.set_wait_for_completion(execution["wait_for_completion"])
                        if "error_handling" in execution:
                            node.set_error_handling(execution["error_handling"])
                
                elif node_type == "wait":
                    node = WaitNode(node_id, description)
                    if "config" in node_data:
                        config = node_data["config"]
                        if "duration" in config:
                            node.set_duration(config["duration"])
                        if "event" in config:
                            node.set_event(config["event"])
                
                else:
                    # For unsupported node types, create a generic node
                    # In a real implementation, all node types would be supported
                    from core.node import Node
                    class GenericNode(Node):
                        def execute(self, context):
                            return {"status": "completed", "message": "Generic node executed"}
                    
                    node = GenericNode(node_id, node_type, description)
                
                # Set inputs and outputs
                for input_var in node_data.get("input", []):
                    node.add_input(input_var)
                
                for output_var in node_data.get("output", []):
                    node.add_output(output_var)
                
                # Set observability
                if "observability" in node_data:
                    observability = node_data["observability"]
                    for metric in observability.get("metrics", []):
                        node.add_metric(metric)
                    if "log_level" in observability:
                        node.set_log_level(observability["log_level"])
                
                workflow.add_node(node)
        
        # Parse flow
        if "flow" in workflow_data:
            flow_data = workflow_data["flow"]
            
            # Set process information
            if "process" in flow_data:
                process = flow_data["process"]
                workflow.flow["process"] = {
                    "name": process.get("name", workflow.name),
                    "description": process.get("description", workflow.description),
                    "start_at": process.get("start_at")
                }
            
            # Set entry points
            if "entry_points" in flow_data:
                workflow.flow["entry_points"] = flow_data["entry_points"]
            
            # Set states
            if "states" in flow_data:
                workflow.flow["states"] = flow_data["states"]
        
        # Set the rest of the sections as-is
        for section in ["dynamic_flow", "imports", "transition_points", 
                        "communication", "context", "error_handling", "monitoring"]:
            if section in workflow_data:
                setattr(workflow, section, workflow_data[section])
        
        return workflow