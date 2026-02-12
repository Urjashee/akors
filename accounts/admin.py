from django.contrib import admin
from .models import User, Role, Title, Subscriptions, PasswordResets

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Title)
admin.site.register(Subscriptions)
admin.site.register(PasswordResets)
