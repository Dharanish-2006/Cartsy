from django.db import models
from authentication.models import User

class Widget(models.Model):
    name = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=50)
    content = models.TextField(default='Widget Content')

    def __str__(self):
        return self.name


class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    layout = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}'s Dashboard"


class Alert(models.Model):
    type = models.CharField(max_length=255)
    message = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.type}: {self.message}"
