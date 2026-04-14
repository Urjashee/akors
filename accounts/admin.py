from django.contrib import admin

from forms.models import Forms
from property.models import Images, PropertyManagement, PropertyForms, Unit, UnitForm, State, UnitType, UnitClass
from .models import User, Role, Title, Subscriptions, PasswordResets, RefreshToken

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Title)
admin.site.register(State)
admin.site.register(Subscriptions)
admin.site.register(PasswordResets)
admin.site.register(RefreshToken)
admin.site.register(Forms)
admin.site.register(Images)
admin.site.register(PropertyManagement)
admin.site.register(PropertyForms)
admin.site.register(Unit)
admin.site.register(UnitForm)
admin.site.register(UnitType)
admin.site.register(UnitClass)
