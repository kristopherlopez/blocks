from typing import Dict, Any
from core.node import Node

class NotificationNode(Node):
    """Sends notifications to users or systems."""
    
    def __init__(self, node_id: str, description: str = ""):
        super().__init__(node_id, "notification", description)
    
    def set_channel(self, channel: str) -> None:
        """Set the notification channel (email, sms, slack, etc.)."""
        self.set_config("channel", channel)
    
    def set_template(self, template: str) -> None:
        """Set the notification template."""
        self.set_config("template", template)
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set the data to be used in the notification template."""
        self.set_config("data", data)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the notification logic."""
        channel = self.config.get("channel", "email")
        template = self.config.get("template", "")
        data = self.config.get("data", {})
        
        # Merge context with notification data
        merged_data = {**data}
        for key, value in context.items():
            if key not in merged_data:
                merged_data[key] = value
        
        # In a real implementation, this would use a notification service
        # to send the notification via the specified channel
        from engine.expression_evaluator import ExpressionEvaluator
        
        # Process the template with the merged data
        if template:
            processed_template = ExpressionEvaluator.replace_expressions(template, merged_data)
        else:
            processed_template = "No template specified"
        
        return {
            "status": "sent",
            "channel": channel,
            "message": processed_template
        }