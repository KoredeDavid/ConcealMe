from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^[\w]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and underscore.'
    )
    flags = 0


username_validator = UnicodeUsernameValidator()


class CustomUser(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=30,
        help_text=_('Letters, digits and underscore only.'),
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=False, null=True, unique=True)
    senders_view = models.BooleanField(blank=True, default=False)

    def clean(self):
        self.username = self.username.capitalize()
        self.email = self.email.lower()


class Messages(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    ip_address = models.GenericIPAddressField()
    text = models.TextField(max_length=300)
    date_sent = models.DateTimeField(auto_now_add=True)
    likes = models.BooleanField(blank=True, default=False)
    archives = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.text


class Telegram(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    telegram_id = models.PositiveIntegerField()
    anon_user_id = models.TextField()
    telegram_switch = models.BooleanField(blank=True, default=False)
    telegram_choice = models.CharField(blank=True, default="3", max_length=1)

    def __str__(self):
        return self.anon_user_id + ' ' + str(self.telegram_id)


class Feedback(models.Model):
    name = models.CharField(max_length=25, help_text="Name of the sender")
    subject = models.CharField(max_length=40, help_text="Name of the sender")
    email = models.EmailField(max_length=100)
    message = models.TextField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Feedback"

    def __str__(self):
        return self.name + "_" + self.email

