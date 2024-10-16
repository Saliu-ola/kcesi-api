from django.db import models
class Organization(models.Model):
    name = models.CharField(max_length=50, null=True)
    organization_id = models.CharField(max_length=15, null=True,unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.name or " "

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=['organization_id'], name='unique_organization_id_per_organization')
        ]
