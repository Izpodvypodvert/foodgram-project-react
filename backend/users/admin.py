from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import Subscription, User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role', 'username', 'email', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'first_name',
                           'last_name', 'email')}),
        ('Permissions', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'first_name',
                'last_name', 'role',

            )}
         ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    search_fields = ('author__username', 'subscriber__username')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
