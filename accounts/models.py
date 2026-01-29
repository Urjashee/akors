from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class Title(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "titles"

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class Subscriptions(models.Model):
    name = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()
    external_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "subscriptions"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    qei_number = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=100)
    company_address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=100)

    email_verified_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    title = models.ForeignKey(Title, on_delete=models.PROTECT, related_name="users", null=True, blank=True)
    subscription = models.ForeignKey(Subscriptions, on_delete=models.PROTECT, related_name="users", null=True, blank=True)

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"

class PasswordResets(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    type = models.IntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "password_resets"