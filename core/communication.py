from typing import Dict, List, Any, Optional, Callable
import uuid
import time
import threading
from collections import deque

class Channel:
    """Represents a communication channel between agents."""
    
    def __init__(self, channel_id: str, channel_type: str = "direct"):
        self.id = channel_id
        self.type = channel_type  # direct, broadcast, selective
        self.participants: List[str] = []
        self.message_queue = deque()
        self._lock = threading.Lock()
    
    def add_participant(self, agent_id: str) -> None:
        """Add a participant to the channel."""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
    
    def send_message(self, sender: str, content: Any, recipients: Optional[List[str]] = None) -> str:
        """
        Send a message through the channel.
        
        Args:
            sender: The agent sending the message
            content: The message content
            recipients: Optional list of specific recipients (for selective channels)
            
        Returns:
            A message ID
        """
        if sender not in self.participants:
            raise ValueError(f"Agent {sender} is not a participant in channel {self.id}")
        
        # For selective channels, validate recipients
        if self.type == "selective" and recipients:
            for recipient in recipients:
                if recipient not in self.participants:
                    raise ValueError(f"Agent {recipient} is not a participant in channel {self.id}")
        
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "sender": sender,
            "recipients": recipients if self.type == "selective" else None,
            "content": content,
            "timestamp": time.time(),
            "read_by": []
        }
        
        with self._lock:
            self.message_queue.append(message)
        
        return message_id
    
    def get_messages(self, agent_id: str, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """
        Get messages for an agent.
        
        Args:
            agent_id: The agent requesting messages
            mark_as_read: Whether to mark messages as read
            
        Returns:
            A list of messages
        """
        if agent_id not in self.participants:
            raise ValueError(f"Agent {agent_id} is not a participant in channel {self.id}")
        
        messages = []
        with self._lock:
            for message in self.message_queue:
                # Check if the message is addressed to this agent
                if (self.type == "broadcast" or 
                    (self.type == "direct" and message["sender"] != agent_id) or
                    (self.type == "selective" and message["recipients"] and agent_id in message["recipients"])):
                    
                    # Don't include messages sent by this agent in direct channels
                    if self.type == "direct" and message["sender"] == agent_id:
                        continue
                    
                    messages.append(message.copy())
                    
                    # Mark as read if requested
                    if mark_as_read and agent_id not in message["read_by"]:
                        message["read_by"].append(agent_id)
        
        return messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the channel to a dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "participants": self.participants
        }

class Protocol:
    """Defines a communication protocol for agents."""
    
    def __init__(self, protocol_id: str, protocol_type: str = "request-response"):
        self.id = protocol_id
        self.type = protocol_type  # request-response, publish-subscribe
        self.message_format: Optional[str] = None
        self.handlers: Dict[str, Callable] = {}
    
    def set_message_format(self, schema_ref: str) -> None:
        """Set the message format schema reference."""
        self.message_format = schema_ref
    
    def register_handler(self, event: str, handler: Callable) -> None:
        """Register a handler for a protocol event."""
        self.handlers[event] = handler
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the protocol to a dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "message_format": self.message_format
        }

class CommunicationManager:
    """Manages communication channels and protocols between agents."""
    
    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.protocols: Dict[str, Protocol] = {}
    
    def create_channel(self, channel_id: str, channel_type: str = "direct") -> Channel:
        """Create a new communication channel."""
        channel = Channel(channel_id, channel_type)
        self.channels[channel_id] = channel
        return channel
    
    def create_protocol(self, protocol_id: str, protocol_type: str = "request-response") -> Protocol:
        """Create a new communication protocol."""
        protocol = Protocol(protocol_id, protocol_type)
        self.protocols[protocol_id] = protocol
        return protocol
    
    def get_channel(self, channel_id: str) -> Channel:
        """Get a communication channel by ID."""
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} does not exist")
        return self.channels[channel_id]
    
    def get_protocol(self, protocol_id: str) -> Protocol:
        """Get a communication protocol by ID."""
        if protocol_id not in self.protocols:
            raise ValueError(f"Protocol {protocol_id} does not exist")
        return self.protocols[protocol_id]
    
    def send_message(self, channel_id: str, sender: str, content: Any, 
                    recipients: Optional[List[str]] = None) -> str:
        """Send a message through a channel."""
        channel = self.get_channel(channel_id)
        return channel.send_message(sender, content, recipients)
    
    def get_messages(self, channel_id: str, agent_id: str, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """Get messages for an agent from a channel."""
        channel = self.get_channel(channel_id)
        return channel.get_messages(agent_id, mark_as_read)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the communication manager configuration to a dictionary representation."""
        return {
            "channels": {channel_id: channel.to_dict() for channel_id, channel in self.channels.items()},
            "protocols": {protocol_id: protocol.to_dict() for protocol_id, protocol in self.protocols.items()}
        }