from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class UserModel(UserAdmin):
    list_display =['username','email','user_type']
    list_filter = ['user_type','is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Advanced', {'fields': ('user_type',)}),
    )
admin.site.register(CustomUser,UserModel)
admin.site.register(Staff)
admin.site.register(Staff_Leave)
