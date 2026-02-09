from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    """
    Messages privés ou globaux.
    - if recipient is None -> global message
    - if recipient is set -> private message
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        if self.recipient:
            return f"Private: {self.sender.username} -> {self.recipient.username}"
        return f"Global: {self.sender.username}"
