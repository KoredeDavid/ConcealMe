import json
import os

from secrets import token_urlsafe

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .form import (CustomPasswordChangeForm, CustomUserChangeForm,
                   CustomUserCreationForm, MyMessages, TelegramForm, FeedbackForm)
from .models import CustomUser, Messages, Telegram

from django.core.mail import mail_admins


# Create your views here.
@require_POST
@csrf_exempt
def get_last_chat_id_and_text(request):
    try:
        updates = json.loads(request.body)
        text = updates["message"]["text"]
        chat_id = updates["message"]["chat"]["id"]
        chat_id = str(chat_id)
        print(text)
        if text in CustomUser.objects.all().values_list('anon_user_id', flat=True):
            print('im alive')
            from .telegram import send_telegram_message2
            url = os.environ.get('WEB_URL', "")
            my_username = str(CustomUser.objects.get(anon_user_id=text).username)
            exists = CustomUser.objects.filter(username=my_username, anon_user_id=text).exists() and Telegram.objects.filter(user__username=my_username, telegram_id=chat_id).exists()
            if not exists:
                print(text)
                if str(CustomUser.objects.get(username=my_username).anon_user_id) == text:
                    print('big deal')
                    update = Telegram.objects.get(user__username=my_username)
                    update.telegram_id = chat_id
                    update.telegram_switch = True
                    update_anon_user_id = CustomUser.objects.get(username=my_username, anon_user_id=text)
                    if "-" in str(chat_id):
                        update_anon_user_id.anon_user_id = f"Anon-{my_username}-{token_urlsafe(10)}"
                    update_anon_user_id.save()
                    print('saved1')
                    update.save()
                    print('saved2')
                    print(text + ' ' + str(chat_id))
                    send_telegram_message2(
                        'Welcome 👑{}, you will receive 3 anonymous messages per notification on your telegram '
                        'account. '
                        'Access, {} to edit your '
                        'telegram settings. Share your link ({}) to your friends and let them shake tables😀'.format
                        (my_username, url + my_username + '/telegram', url + my_username), str(chat_id))
            else:
                print('bla')
                send_telegram_message2('👑{}, your telegram chat id has already been registered. Access, '
                                       '{} to edit your '
                                       'telegram settings.'.format(my_username, url + my_username + '/telegram'),
                                       str(chat_id))
    except:
        pass
    return HttpResponse('OK')


def home(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            sender = form.cleaned_data['email']
            subject = "You have a new Feedback from {}:{}".format(name, sender)
            message = "Subject: {}\n\nMessage: {}".format(form.cleaned_data['subject'], form.cleaned_data['message'])
            mail_admins(subject, message, fail_silently=False)
            form.save()
            messages.success(request, 'Message Sent')
            return redirect('/#contact')
    else:
        if request.user.is_authenticated:
            return redirect('anon:dashboard', request.user.username)
        form = FeedbackForm()
    return render(request, 'home.html', {"form": form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        telegram_form = TelegramForm(request.POST)
        invalid = ['Anonymous', 'Fuck', 'Bitch', 'Login', 'Logout', 'Register', 'Reset', 'Admin', 'Feedback']
        if form.is_valid() and telegram_form.is_valid():
            obj_form = form.save(commit=False)
            if obj_form.username in invalid:
                messages.error(request, '"{}" cannot be used as a username'.format(obj_form.username))
                return render(request, 'register.html', {'form': form})
            else:
                obj_form.save()
            t_form = telegram_form.save(commit=False)
            my_username = form.cleaned_data.get('username')
            user = CustomUser.objects.get(username__iexact=my_username)
            user_id = CustomUser.objects.get(username__iexact=my_username).id
            # t_form.anon_user_id = 'Anon-{}-{}-{}'.format(my_username, user_id, token_urlsafe(10))
            t_form.user = user
            t_form.telegram_id = '0'
            t_form.save()
            password = form.cleaned_data.get('password1')
            login_user = authenticate(username=user, password=password)
            login(request, login_user)
            return redirect('anon:dashboard', request.user.username)
    else:
        form = CustomUserCreationForm()
        # telegram_form = TelegramForm()
    return render(request, 'Register.html', {'form': form})


def sign_in(request):
    # if request.user.is_authenticated:
    # return render(request, 'home.html')   
    nexts = request.GET.get('next')
    print(nexts)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == "" or password == "":
            messages.error(request, 'Both username/email and password must be filled')
            return render(request, 'login.html')
        try:
            username = CustomUser.objects.get(username__iexact=username).username
        except CustomUser.DoesNotExist:
            pass
        user = authenticate(request=request, username=str(username), password=password)
        if nexts is None:
            if user is not None:
                login(request, user)
                return redirect('anon:dashboard', request.user.username)
            else:
                messages.error(request, 'Guy, your login details are incorrect')
                return render(request, 'login.html')
        elif user is not None:
            login(request, user)
            return redirect(nexts)
        else:
            messages.error(request, 'Guy, your login details are incorrect')
            return render(request, 'login.html')

    else:
        # form = AuthenticationForm()
        return render(request, 'login.html')


@login_required(login_url='anon:sign_in')
def update_profile(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            update = CustomUserChangeForm(request.POST, instance=user)
            if update.is_valid():
                update.save()
                """
                update_anon_user_id = Telegram.objects.get(user__id=user.id)
                update_anon_user_id.anon_user_id = 'Anon-{}-{}-{}'.format(new_user, user.id, token_urlsafe(10))
                update_anon_user_id.save()
                """
                new_user = CustomUser.objects.get(id=user.id).username
                messages.success(request, 'Profile updated successfully')
                return redirect('anon:dashboard', new_user)
        else:
            update = CustomUserChangeForm(instance=user)
        return render(request, 'update-profile.html', {'update': update})
    else:
        messages.error(request, 'You are not authorized to access that page')
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def change_password(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            update = CustomPasswordChangeForm(user, request.POST)
            if update.is_valid():
                update_password = update.save()
                update_session_auth_hash(request, update_password)
                messages.success(request, 'Password changed successfully')
                return redirect('anon:dashboard', my_username)
        else:
            update = CustomPasswordChangeForm(user)
        return render(request, 'change-password.html', {'update': update, 'user': user})
    else:
        messages.error(request, 'You are not authorized to access that page')
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def dashboard(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        anon_user_id = CustomUser.objects.get(username=user).anon_user_id
        message = Messages.objects.filter(user=user, archives=False).order_by('-date_sent')
        zero = Telegram.objects.get(user=user).telegram_id == "0"
        switch = Telegram.objects.get(user=user).telegram_switch
        archives = Messages.objects.filter(user=user, archives=True).order_by('-date_sent')
        count_archives = archives.count() != 0
        view = user.senders_view
        url = os.environ.get('WEB_URL', "")
        page = request.GET.get('page', 1)
        paginator = Paginator(message, 10)
        try:
            message = paginator.page(page)
        except PageNotAnInteger:
            message = paginator.page(1)
        except EmptyPage:
            message = paginator.page(paginator.num_pages)
        context = {
            'zero': zero,
            'switch': switch,
            'user': user,
            'message': message,
            'anon_user_id': anon_user_id,
            'archives': count_archives,
            'view': view,
            'url': url
        }
        return render(request, 'dashboard.html', context)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def senders_view(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            if not user.senders_view:
                user.senders_view = True
                user.save()
            else:
                user.senders_view = False
                user.save()
            return HttpResponse('Success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:home')
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def like_post(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            message = get_object_or_404(Messages, user=user, id=message_id)
            if message.likes:
                message.likes = False
                message.save()
            else:
                message.likes = True
                message.save()
            return HttpResponse('Success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:home')
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def like_post_list(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        favourites = Messages.objects.filter(user=user, likes=True)
        page = request.GET.get('page', 1)
        paginator = Paginator(favourites, 10)
        try:
            favourites = paginator.page(page)
        except PageNotAnInteger:
            favourites = paginator.page(1)
        except EmptyPage:
            favourites = paginator.page(paginator.num_pages)

        # favourites = message.archives
        return render(request, 'favourites.html', {'message': favourites, 'user': user})
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def archive_post(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            user_id = user.id
            message = get_object_or_404(Messages, user=user, id=message_id)
            if message.archives:
                message.archives = False
                message.save()
            else:
                message.archives = True
                message.save()
            return HttpResponse('Success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:home')
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def archive_list(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        archives = Messages.objects.filter(user=user, archives=True)
        page = request.GET.get('page', 1)
        paginator = Paginator(archives, 10)
        try:
            archives = paginator.page(page)
        except PageNotAnInteger:
            archives = paginator.page(1)
        except EmptyPage:
            archives = paginator.page(paginator.num_pages)

        # archives = user.archives.all()
        return render(request, 'archives.html', {'message': archives, 'user': user})
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def delete_message(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            message = Messages.objects.get(user=user, id=message_id)
            message.delete()
            return HttpResponse('success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        zero = Telegram.objects.get(user=user).telegram_id == "0"
        telegram_id = CustomUser.objects.get(username=user).anon_user_id
        switch = Telegram.objects.get(user=user).telegram_switch
        choice = Telegram.objects.get(user=user).telegram_choice
        context = {
            'zero': zero,
            'switch': switch,
            'user': user,
            'choice': choice,
            'id': telegram_id
        }

        return render(request, 'telegram.html', context)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def deactivate_telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            switch = Telegram.objects.get(user=user)
            switch.telegram_switch = False
            switch.save()
            messages.success(request, "Telegram Deactivated")
            return redirect('anon:telegram', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def activate_telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            switch = Telegram.objects.get(user=user)
            switch.telegram_switch = True
            switch.save()
            messages.success(request, "Telegram Activated")
            return redirect('anon:dashboard', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def telegram_choice(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user.username)
        if request.method == 'POST':
            choice = Telegram.objects.get(user=user)
            choice.telegram_choice = request.POST['telegram_choice']
            choice.save()
            messages.success(request, "Done")
            return redirect('anon:telegram', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user.username))
        return redirect("anon:sign_in")


def send_message(request, my_username):
    try:
        user = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()

    view = user.senders_view
    url = os.environ.get('WEB_URL', "")
    message = Messages.objects.filter(user__username__iexact=my_username, archives=False).order_by('-date_sent')
    page = request.GET.get('page', 1)
    paginator = Paginator(message, 10)
    try:
        message = paginator.page(page)
    except PageNotAnInteger:
        message = paginator.page(1)
    except EmptyPage:
        message = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = MyMessages(request.POST)
        context = {
            'form': form,
            'user': user,
            'view': view,
            'message': message
        }
        if form.is_valid():
            f = form.save(commit=False)
            f.user = user
            f.date_sent = timezone.now()
            f.ip_address = request.META.get("REMOTE_ADDR", '127.0.0.1')
            f.device = request.META.get("HTTP_USER_AGENT", 'Fucks')
            f.save()
            messages.success(request,
                             'Message sent to 👑{}'.format(
                                 user))
            chat = Telegram.objects.get(user__username__iexact=my_username).telegram_id
            from .telegram import send_telegram_message
            # sent = message[-4]
            # send = list(set(message) ^ set(sent))
            telegram_choices = Telegram.objects.get(user=user).telegram_choice
            if Telegram.objects.get(user=user).telegram_switch:
                message = Messages.objects.filter(user__username__iexact=my_username, archives=False).order_by(
                    '-date_sent')
                count = len(message)
                choice = int(telegram_choices)

                if count % int(telegram_choices) == 0:
                    amount_of_messages_to_send = (message[:choice][::-1])
                    amount_of_messages_to_send.insert(0, f"{user}👑 anonymous messages, from conceal.🙈")
                    amount_of_messages_to_send.append(f"This is your link {url}{user} 👑")
                    send_telegram_message(amount_of_messages_to_send, chat)

            return redirect("/{}/#home".format(user))
    else:
        form = MyMessages()
    context = {
        'form': form,
        'user': user,
        'view': view,
        'message': message
    }
    return render(request, 'send_message.html', context)


def sign_out(request):
    logout(request)
    messages.success(request, 'Logged Out Successfully  👑Sire')
    return redirect("anon:sign_in")
