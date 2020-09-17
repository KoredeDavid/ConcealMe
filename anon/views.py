import json
from _socket import gaierror
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
        if text in Telegram.objects.all().values_list('anon_user_id', flat=True):
            from .telegram import send_telegram_message2
            url = 'https://bbd6b1f1b201.ngrok.io/'
            my_username = str(Telegram.objects.get(anon_user_id = text).user)
            exists = Telegram.objects.filter(user__username__iexact=my_username, telegram_id=chat_id, anon_user_id=text).exists()
            if not exists:
                if Telegram.objects.get(user__username__iexact=my_username).anon_user_id == text:
                    update = Telegram.objects.get(user__username__iexact=my_username)
                    update.telegram_id = chat_id
                    update.telegram_switch = True
                    update.save()
                    print(text + ' ' + str(chat_id))
                    send_telegram_message2(
                        'Welcome {}, you will receive 3 anonymous messages per notification on your telegram account. '
                        'Access, {} to edit your '
                        'telegram settings. Share your link ({}) to your friends and let them shake tables'.format
                        (my_username, url + my_username + '/telegram', url+my_username), chat_id)
            else:
                send_telegram_message2('{}, your telegram chat id has already been registered. Access, {} to edit your '
                                      'telegram settings.'.format(my_username, url+my_username+'/telegram'), chat_id)

    except json.decoder.JSONDecodeError as err:
        return HttpResponse(str(err))
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
            t_form.anon_user_id = 'Anon-{}-{}-{}'.format(my_username, user_id, token_urlsafe(10))
            t_form.user = user
            t_form.telegram_id = 0
            t_form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('anon:dashboard', request.user)
    else:
        form = CustomUserCreationForm()
        # telegram_form = TelegramForm()
    return render(request, 'register.html', {'form': form})


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
        user = authenticate(request=request, username=username, password=password)
        if nexts is None:
            if user is not None:
                login(request, user)
                return redirect('anon:dashboard', request.user)
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
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            update = CustomUserChangeForm(request.POST, instance=user)
            if update.is_valid():
                update.save()
                update_anon_user_id = Telegram.objects.get(user__id=user.id)
                new_user = CustomUser.objects.get(id=user.id).username
                old_id = update_anon_user_id.anon_user_id
                Anon, my_username, pk, token = old_id.split('-')
                update_anon_user_id.anon_user_id = 'Anon-{}-{}-{}'.format(new_user, user.id, token)
                update_anon_user_id.save()
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
        user = get_object_or_404(CustomUser, username__iexact=request.user)
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
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        anon_user_id = Telegram.objects.get(user__username__iexact=user).anon_user_id
        message = Messages.objects.filter(user__username__iexact=user, archives=False).order_by('-date_sent')
        zero = Telegram.objects.get(user__username__iexact=user).telegram_id == 0
        switch = Telegram.objects.get(user__username__iexact=user).telegram_switch
        archives = Messages.objects.filter(user__username__iexact=user, archives=True).order_by('-date_sent')
        count_archives = archives.count() != 0
        view = user.senders_view
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
            'view': view
        }
        return render(request, 'dashboard.html', context)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def senders_view(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            message = get_object_or_404(CustomUser, username__iexact=user)
            if not message.senders_view:
                message.senders_view = True
                message.save()
            else:
                message.senders_view = False
                message.save()
            return HttpResponse('Success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:home')
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def like_post(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            user_id = user.id
            message = get_object_or_404(Messages, user__username__iexact=user, id=message_id)
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
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def like_post_list(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        favourites = Messages.objects.filter(user__username__iexact=user, likes=True)
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
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def archive_post(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            user_id = user.id
            message = get_object_or_404(Messages, user__username__iexact=user, id=message_id)
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
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def archive_list(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        archives = Messages.objects.filter(user__username__iexact=user, archives=True)
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
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


"""
@login_required(login_url='anon:sign_in')
def archive(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            message = Messages.objects.get(user__username__iexact=user, id=message_id)
            pk = message.pk
            m_id = message.id
            username = message.user
            text = message.text
            ip_address = message.ip_address
            date_sent = message.date_sent
            archive_message = Archive.objects.create(user=username, id=m_id, pk=pk, text=text,
                                                     date_sent=date_sent, ip_address=ip_address)
            archive_message.save()
            message.delete()
            return HttpResponse('success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:home')
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def un_archive(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            archived = Archive.objects.get(user__username__iexact=user, id=message_id)
            pk = archived.pk
            m_id = archived.id
            username = archived.user
            text = archived.text
            ip_address = archived.ip_address
            date_sent = archived.date_sent
            un_archive_message = Messages.objects.create(user=username, id=m_id, pk=pk, text=text,
                                                         date_sent=date_sent, ip_address=ip_address)
            un_archive_message.save()
            archived.delete()
            return HttpResponse('success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")

@login_required(login_url='anon:sign_in')
def delete_archive(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            message = Archive.objects.get(user__username__iexact=user, id=message_id)
            message.delete()
            return HttpResponse('success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def archive_list(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        archives = Archive.objects.filter(user__username__iexact=user).order_by('-date_sent')
        page = request.GET.get('page', 1)
        paginator = Paginator(archives, 10)
        try:
            archives = paginator.page(page)
        except PageNotAnInteger:
            archives = paginator.page(1)
        except EmptyPage:
            archives = paginator.page(paginator.num_pages)
        context = {
            'message': archives,
            'user': user
        }
        return render(request, 'archives.html', context=context)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")

"""


@login_required(login_url='anon:sign_in')
def delete_message(request, my_username, message_id):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            message = Messages.objects.get(user__username__iexact=user, id=message_id)
            message.delete()
            return HttpResponse('success')
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        zero = Telegram.objects.get(user__username__iexact=user).telegram_id == 0
        telegram_id = Telegram.objects.get(user__username__iexact=user).anon_user_id
        switch = Telegram.objects.get(user__username__iexact=user).telegram_switch
        choice = Telegram.objects.get(user__username__iexact=user).telegram_choice
        context = {
            'zero': zero,
            'switch': switch,
            'user': user,
            'choice': choice,
            'id': telegram_id
        }

        return render(request, 'telegram.html', context)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def deactivate_telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            switch = Telegram.objects.get(user__username__iexact=user)
            switch.telegram_switch = False
            switch.save()
            messages.success(request, "Telegram Deactivated")
            return redirect('anon:telegram', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def activate_telegram(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            switch = Telegram.objects.get(user__username__iexact=user)
            switch.telegram_switch = True
            switch.save()
            messages.success(request, "Telegram Activated")
            return redirect('anon:dashboard', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


@login_required(login_url='anon:sign_in')
def telegram_choice(request, my_username):
    try:
        valid = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    if request.user.is_authenticated and request.user == valid:
        user = get_object_or_404(CustomUser, username__iexact=request.user)
        if request.method == 'POST':
            choice = Telegram.objects.get(user__username__iexact=user)
            choice.telegram_choice = request.POST['telegram_choice']
            choice.save()
            messages.success(request, "Done")
            return redirect('anon:telegram', my_username)
        else:
            messages.error(request, "👑Alaye, it doesn't work that way ")
            return redirect('anon:dashboard', user)
    else:
        messages.error(request, 'You are  logged in as {}'.format(request.user))
        return redirect("anon:sign_in")


def send_message(request, my_username):
    try:
        user = CustomUser.objects.get(username__iexact=my_username)
    except CustomUser.DoesNotExist:
        raise Http404()
    view = user.senders_view
    page = request.GET.get('page', 1)
    message = Messages.objects.filter(user__username__iexact=my_username, archives=False).order_by('-date_sent')
    paginator = Paginator(message, 10)
    try:
        message = paginator.page(page)
    except PageNotAnInteger:
        message = paginator.page(1)
    except EmptyPage:
        message = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = MyMessages(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.user = user
            f.date_sent = timezone.now()
            f.ip_address = '192.168.0.1'
            f.save()
            messages.success(request,
                             'Message sent to 👑{}'.format(
                                 user))
            chat = Telegram.objects.get(user__username__iexact=my_username).telegram_id
            from .telegram import send_telegram_message
            # sent = message[-4]
            # send = list(set(message) ^ set(sent))
            telegram_choices = Telegram.objects.get(user__username__iexact=user).telegram_choice
            if Telegram.objects.get(user__username__iexact=user).telegram_switch:
                if len(message) % int(telegram_choices) == 0:
                    send_telegram_message((message[:int(telegram_choices)][::-1]), chat)
            form = MyMessages()
            context = {
                'form': form,
                'user': user,
                'view': view,
                'message': message
            }
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


"""
    $('#like{{ message.id }}').toggleClass(' fa fa-heart button-one float-left');
    if request.is_ajax():
        html = render_to_string('dashboard.html', request=request)
        return JsonResponse({'form': html}) 
    <div id="{{message.id}}">
        {% include 'like_post.html' with message=message %}
    </div>
    {% load static %}
    {% load custom_tags %}

    {% liked user message.id as liked %}
       <form  action=""  method="post">
        {% if message.liked %}
            {% csrf_token %}
            <button type="submit" id="like" name="message_id" value="{{ message.id }}"   class=" like fa fa-heart button-one float-left"  style="font-size:24px; color:red; display: inline-block" ></button>
            <script type="text/javascript">
                $(document).ready(function(event){

                $(document).on('click', '#like', function(event){
                  console.log("i'm clicked");
                  event.preventDefault();
                  var pk = $(this).attr('value');
                  // Construct the full URL with "id"
                  $.ajax({
                    type: 'POST',
                    url: "{% url 'anon:like' user message.id %}",
                    data: {'my_username': '{{user}}', 'message_id': pk, 'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    dataType: 'json',
                    success: function(response){
                      $('#'+pk).html(response['form'])
                      console.log($('#'+pk).html(response['form']));
                    },
                    error: function(rs, e){
                      console.log(rs.responseText);
                    },
                  });
                });
                });
            </script>
    {% else %}
            <button type="submit" id="like" name="message_id" value="{{ message.id }}"  class=" like fa fa-heart-o button-one float-left"  style="font-size:24px; color:red; display: inline-block" ></button>
            <script type="text/javascript">
                $(document).ready(function(event){

                $(document).on('click', '#like', function(event){
                  console.log("i'm clicked");
                  event.preventDefault();
                  var pk = $(this).attr('value');
                  // Construct the full URL with "id"
                  $.ajax({
                    type: 'POST',
                    url: "{% url 'anon:like' user message.id %}",
                    data: {'my_username': '{{user}}', 'message_id': {{message.id}}, 'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    dataType: 'json',
                    success: function(response){
                      $('#'+pk).html(response['form'])
                      console.log($('#'+pk).html(response['form']));
                    },
                    error: function(rs, e){
                      console.log(rs.responseText);
                    },
                  });
                });
                });
            </script>
    {% endif %}
       </form>
                    
"""

'''
    {% empty %}

                <div style=" margin: auto;
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            -ms-transform: translate(-50%, -50%);
                            transform: translate(-50%, -50%);
                            background-color: #fffdd0;" >

                    <div class="card" style="width:40rem; height:30rem; background-color: ;">
                        <div class="card-body  border border-light p-5 text-center">
                            <br><br><br><br><br>
                            <div class="d-flex justify-content-around ">
                                <h3 class="text-center">You got no message yet</h3>
                            </div>
                            <div class='container ' style="color:black; text-align:centre;">
                                <i class="fa fa-heart" style="font-size:100px; color:red; display: inline-block"></i>
                            </div>
                        </div>
                    </div>
               </div>
            {% endfor %}
            {% if archives %}
               <form  class="text-center" action="{% url 'anon:archive_list' user %}">  <button ><span style=" background-color: white; "><b>ARCHIVES</b><img style="width:35px; height:35px; display: inline-block" src="{% static 'images/archive.png' %}" alt="" class="img-fluid"></span></button></form>
            {%endif%}
    
    try:
        if len(updates["result"]) > 0:
            num_updates = len(updates["result"])
            last_update = num_updates - 1
            text = updates["result"][last_update]["message"]["text"]
            chat_id = updates["result"][last_update]["message"]["chat"]["id"]
            if text in Telegram.objects.all().values_list('anon_user_id', flat=True):
                Anon, my_username, pk = text.split('-')
                if Telegram.objects.get(user__username__iexact=my_username).anon_user_id == text:
                    update = Telegram.objects.get(user__username__iexact=my_username)
                    update.telegram_id = chat_id
                    update.telegram_switch = True
                    update.save()
                    return HttpResponse(text, chat_id)
    except :
        return HttpResponseBadRequest('Nothing yet')
'''
