from django.db import models

# Example model (not required for UI). Remove or modify as needed.
class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
