from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from anon_api import views


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="ConcealMe API",
        default_version='v1',
        description="An API that allows you to access your ConcealMe Data",
        terms_of_service="https://concealme.herokuapp.com/",
        contact=openapi.Contact(email="mrconceal@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


app_name = 'anon_api'

router = DefaultRouter()
router.register('', views.MessageView, basename='message')

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('auth/register/', views.register),
    path('auth/login/', obtain_auth_token),

    path('auth/reset_password/', views.PasswordResetView.as_view()),
    path('auth/reset/<uidb64>/<token>/', views.SetPasswordView.as_view()),

    path('telegram/', views.TelegramView.as_view(),),

    path('message/', include(router.urls)),
    path('message/archive/<id>', views.ArchiveMessageView.as_view()),
    path('message/unarchive/<id>', views.UnArchiveMessageView.as_view()),
    path('message/like/<id>', views.LikeMessageView.as_view()),
    path('message/unlike/<id>', views.UnLikeMessageView.as_view()),
]
