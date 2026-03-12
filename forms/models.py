from django.db import models

from property.models import State


class Forms(models.Model):
    name = models.CharField(max_length=500)
    image = models.ImageField(upload_to="forms/", null=True, blank=True)

    # expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    state = models.ForeignKey(State, on_delete=models.PROTECT, null=True)
    # user = models.ForeignKey(User, on_delete=models.PROTECT)
    # unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    # property = models.ForeignKey(PropertyManagement, on_delete=models.CASCADE)

    class Meta:
        db_table = "forms"
