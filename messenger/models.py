from django.db import models
import os


class MessageBatch(models.Model):
    """Tracks a batch of messages from one Excel upload"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    excel_filename = models.CharField(max_length=255)
    total_messages = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Batch {self.id} - {self.excel_filename} ({self.status})"
    
    @property
    def progress_percent(self):
        if self.total_messages == 0:
            return 0
        return int((self.sent_count + self.failed_count) / self.total_messages * 100)


class Message(models.Model):
    """Individual message to be sent"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    batch = models.ForeignKey(MessageBatch, on_delete=models.CASCADE, related_name='messages')
    phone_number = models.CharField(max_length=20)
    message_text = models.TextField()
    attachment_filename = models.CharField(max_length=255, blank=True, null=True)
    attachment_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.status}"
    
    @property
    def has_attachment(self):
        return bool(self.attachment_path and os.path.exists(self.attachment_path))
