from django.core.exceptions import ValidationError
from django.db import models


class BadWord(models.Model):
    related_terms = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return str(self.pk)  

    def save(self, *args, **kwargs):
        if BadWord.objects.exists():  
            raise ValidationError("Only one collection is allowed to be saved")
        super().save(*args, **kwargs) 

    class Meta:
        ordering = ["-created_at"]
