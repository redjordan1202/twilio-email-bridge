from abc import ABC, abstractmethod


class SenderInterface(ABC):
    """
    Abstract interface for all senders.
    All Sender plugins must be subclass this interface to be loaded by the PluginLoader
    """
    @abstractmethod
    def send(self, message: dict) -> bool:
        """
        Required abstract method for all senders.
        This method handles sender of the message to the plugins destination

        Args:
            message (dict): Extracted message data

        Returns:
            bool: True on success, False on sending failure
        """
        pass
