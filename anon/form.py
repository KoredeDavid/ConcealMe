from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from .models import Messages, CustomUser, Telegram, Feedback


class MyMessages(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Text"}),
                           max_length=300)

    class Meta:
        model = Messages
        fields = ['text']


class TelegramForm(forms.ModelForm):
    class Meta:
        model = Telegram
        exclude = ('user', 'telegram_id', 'anon_user_id',)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = "__all__"

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "Your Username", 'class': 'form-control', }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': "Your Email", 'class': 'form-control  mt-4', }))

    password1 = forms.CharField(
        label=_("Password:"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': "Password",
            'class': 'form-control  mt-4',
        }),
        # help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': "Repeat your password ",
            'class': 'form-control  mt-4',
        }
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "Your Name", 'class': 'form-control  mb-4', }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': "Your Email", 'class': 'form-control  mb-4', }))

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'autofocus': True, 'placeholder': "Your Old Password",
                   'class': 'form-control  mb-4', }),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'placeholder': "New Password", 'class': 'form-control  mb-4', }),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': "Repeat Your New Password",
                                          'class': 'form-control  mb-4', }),
    )

    class Meta:
        model = CustomUser
        fields = '__all__'
