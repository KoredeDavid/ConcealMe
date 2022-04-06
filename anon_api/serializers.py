from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import SetPasswordForm, _unicode_ci_compare
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from anon.models import Messages, CustomUser, username_validator, Telegram

UserModel = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = serializers.SerializerMethodField('get_username')
    liked = serializers.BooleanField(required=False, default=False)
    archived = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Messages
        fields = '__all__'

    def get_username(self, message):
        username = message.user.username
        return username


class ArchiveLikeMessageSerializer(MessageSerializer):
    liked = serializers.ReadOnlyField()
    archived = serializers.ReadOnlyField()
    text = serializers.ReadOnlyField()


class CustomUserCreationSerializer(serializers.ModelSerializer):
    email_validator_queryset = CustomUser.objects.all().values_list('email', flat=True)
    email_validator_message = "A user with that email already exists"

    email = serializers.EmailField(validators=[
        UniqueValidator(queryset=email_validator_queryset, message=email_validator_message, lookup='iexact')], )
    password1 = serializers.CharField(validators=[validate_password], )
    password2 = serializers.CharField()

    class Meta:
        username_validator_queryset = CustomUser.objects.all().values_list('username', flat=True)
        username_validator_message = "A user with that username already exists"

        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        extra_kwargs = {
            'username': {
                'validators': [
                    UniqueValidator(queryset=username_validator_queryset,
                                    message=username_validator_message, lookup='iexact'),
                    username_validator
                ]
            }
        }

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError({"password2": "Passwords don't match"})
        return attrs

    def save(self):
        user = CustomUser(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )
        user.set_password(self.validated_data['password1'])
        user.save()

        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        return (
            u for u in active_users
            if u.has_usable_password() and
               _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.validated_data["email"]
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            user_email = getattr(user, email_field_name)
            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user_email, html_email_template_name=html_email_template_name,
            )


class SetPasswordSerializer(serializers.Serializer):
    """
    A serializer that lets a user change set their password without entering the old
    password
    """

    new_password1 = serializers.CharField()

    new_password2 = serializers.CharField()

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        password1 = attrs.get('new_password1')
        password2 = attrs.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(
                    {'new_password2': 'The two password fields didn’t match.'},
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return attrs

    def save(self, commit=True):
        password = self.validated_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class TelegramSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = serializers.SerializerMethodField('get_username')

    class Meta:
        model = Telegram
        fields = '__all__'

    def get_username(self, value):
        username = value.user.username
        return username
