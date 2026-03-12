from django.db import models
from accounts.models import User

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "states"

    def __str__(self):
        return self.name

class UnitType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "unit_types"

    def __str__(self):
        return self.name

class UnitClass(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "unit_classes"

    def __str__(self):
        return self.name

class PropertyManagement(models.Model):
    name = models.CharField(max_length=500)
    state_registration = models.CharField(max_length=10)
    property_management_company = models.CharField(max_length=500)
    address_line_1 = models.CharField(max_length=500)
    address_line_2 = models.CharField(max_length=500, null=True)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_properties", null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="created_properties")

    class Meta:
        db_table = "properties"

class Unit(models.Model):
    name = models.CharField(max_length=500)
    state_registration = models.CharField(max_length=10)
    url = models.CharField(max_length=500)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE, null=True)
    unit_class = models.ForeignKey(UnitClass, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    property = models.ForeignKey(PropertyManagement, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "units"


class Images(models.Model):
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    property = models.ForeignKey(PropertyManagement, on_delete=models.CASCADE)

    class Meta:
        db_table = "images"
