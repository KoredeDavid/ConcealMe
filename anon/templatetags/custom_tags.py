from django import template
from ..models import Messages, CustomUser
from django.shortcuts import get_object_or_404

register = template.Library()


@register.simple_tag
def liked(my_username, message_id):
    # user_id = CustomUser.objects.get(username__iexact=my_username).id
    message = get_object_or_404(Messages, user__username__iexact=my_username, id=message_id)

    # if message.likes.filter(id=user_id).exists():
    if message.likes:
        return True
    else:
        return False


@register.simple_tag
def archived(my_username, message_id):
    # user_id = CustomUser.objects.get(username__iexact=my_username).id
    message = get_object_or_404(Messages, user__username__iexact=my_username, id=message_id)

    if message.archives:
        return True
    else:
        return False



