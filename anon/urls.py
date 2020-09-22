from django.urls import path
from . import views
from secrets import token_urlsafe

token = 'torO3ZkNr3o'

app_name = 'anon'

urlpatterns = [
    path('', views.home, name='home'),
    
    path('register/', views.register, name='register'),
    path('login/', views.sign_in, name='sign_in'),   
    path('logout/', views.sign_out, name='sign_out'),

    path('telegram/{}/'.format(token), views.get_last_chat_id_and_text, name='get_updates'),

    path('<my_username>/', views.send_message, name='send_message'),

    path('<my_username>/dashboard/',  views.dashboard, name='dashboard'),
    path('<my_username>/view',  views.senders_view, name='view'),

    path('<my_username>/<message_id>/archive',  views.archive_post, name='archive'),
    path('<my_username>/archives/',  views.archive_list, name='archive_list'),


    path('<my_username>/<message_id>/delete',  views.delete_message, name='delete'),

    path('<my_username>/update-profile/',  views.update_profile, name='update'),
    path('<my_username>/change-password/',  views.change_password, name='password'),

    path('<my_username>/<message_id>/like',  views.like_post, name='like'),
    path('<my_username>/favourites/',  views.like_post_list, name='favourites'),

    path('<my_username>/telegram/', views.telegram, name='telegram'),
    path('<my_username>/telegram/activate', views.activate_telegram, name='activate'),
    path('<my_username>/telegram/deactivate', views.deactivate_telegram, name='deactivate'),
    path('<my_username>/telegram/telegram-choice', views.telegram_choice, name='choice')

]


