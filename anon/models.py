from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator
from secrets import token_urlsafe

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
        validators=[username_validator, MinLengthValidator(5)],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    display_name = models.CharField(max_length=30, editable=False)
    anon_user_id = models.TextField(editable=False)
    email = models.EmailField(_('email address'), blank=False, null=True, unique=True)
    senders_view = models.BooleanField(blank=True, default=False)

    def save(self, *args, **kwargs):
        if self.email is not None:
            self.email = self.email.lower()
        if self.username is not None:
            try:
                user = CustomUser.objects.get(id=self.id).username
            except CustomUser.DoesNotExist:
                user = ''
            if self.username != user:
                self.display_name = self.username
                self.username = self.username.capitalize()
                self.anon_user_id = f'Anon-{self.username}-{self.id}-{token_urlsafe(10)}'
        super().save(*args, **kwargs)
        self.anon_user_id = f'Anon-{self.username}-{self.id}-{token_urlsafe(10)}'
        super().save(*args, **kwargs)


"""
In other to do a reverse many to one query .i.e Trying get or filter an object from the parent key
(In the code below the parent key is CustomUser). Use CustomUser.objects.get(username='Wisdom').messages_set.all()
if  its base model has no 'related_name', else, use its 'relates_name' instead of 'messages_set'.i.e
CustomUser.objects.get(username='Wisdom').user.all()(The related name is 'user')

"""


class Messages(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    ip_address = models.GenericIPAddressField()
    device = models.TextField(default="Fucks")
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
    telegram_id = models.TextField()
    telegram_switch = models.BooleanField(blank=True, default=False)
    telegram_choice = models.CharField(blank=True, default="3", max_length=1)

    def __str__(self):
        return self.user.username + ' ' + str(self.telegram_id)


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
