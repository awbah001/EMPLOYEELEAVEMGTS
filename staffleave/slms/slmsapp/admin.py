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
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'recipient', 'notification_type', 'is_read', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'message', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'message', 'notification_type')
        }),
        ('Users', {
            'fields': ('sender', 'recipient')
        }),
        ('Status', {
            'fields': ('is_read', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(CustomUser,UserModel)
admin.site.register(Employee)
admin.site.register(Employee_Leave)
admin.site.register(Notification, NotificationAdmin)
