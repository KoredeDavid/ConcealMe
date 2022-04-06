from django.contrib import admin
from .models import Messages, Telegram, Feedback
from django.contrib.auth.admin import UserAdmin
from .form import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email', 'anon_user_id', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password',)}),
        (_('Personal info'), {'fields': ('email', 'first_name', 'last_name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),

    )

    readonly_fields = ('last_login', 'date_joined')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('email', 'username')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'date')
    search_fields = ('name', 'email')
    date_hierarchy = 'date'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'date_sent', 'liked', 'archived')
    search_fields = ('user', 'ip_address')
    date_hierarchy = 'date_sent'


class TelegramAdmin(admin.ModelAdmin):
    list_display = ('user',  'telegram_id', 'telegram_switch')
    search_fields = ('user', 'telegram_id')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Messages, MessageAdmin)
admin.site.register(Telegram, TelegramAdmin)
admin.site.register(Feedback, FeedbackAdmin)
