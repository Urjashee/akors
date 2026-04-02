from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

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
    units = models.IntegerField(null=False)
    external_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "subscriptions"

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        from accounts.models import Role

        try:
            admin_role = Role.objects.get(name="Super admin")
        except Role.DoesNotExist:
            raise ValueError("Admin role does not exist. Create it first.")

        user = self.model(
            email=self.normalize_email(email),
            role=admin_role,  # 🔥 FORCE role
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    qei_number = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_address = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)

    email_verified_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    title = models.ForeignKey(Title, on_delete=models.PROTECT, related_name="users", null=True, blank=True)
    subscription = models.ForeignKey(Subscriptions, on_delete=models.PROTECT, related_name="users", null=True, blank=True)
    property = models.ForeignKey("self", on_delete=models.PROTECT, related_name="users", null=True, blank=True)

    objects = UserManager()

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


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1000)
    uuid = models.CharField(max_length=100, null=False, default="UUID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "refresh_tokens"