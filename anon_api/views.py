from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from anon.models import Messages, Telegram
from anon_api.serializers import MessageSerializer, CustomUserCreationSerializer, PasswordResetSerializer, \
    SetPasswordSerializer, TelegramSerializer, ArchiveLikeMessageSerializer


# @api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticated,))
# def messages(request):
#     if request.method == 'GET':
#         user_messages = Messages.objects.filter(user__username=request.user.username).values('id', 'user__username',
#                                                                                              'text',
#                                                                                              'date_sent').order_by(
#             'date_sent')
#         if not user_messages:
#             return Response({"details": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         return Response(user_messages)
#     elif request.method == 'POST':
#         serializer = MessageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(
#                 user=request.user,
#                 date_sent=timezone.now(),
#                 device=request.META.get("HTTP_USER_AGENT", 'Fucks'),
#                 ip_address=request.META.get("REMOTE_ADDR", ),
#             )
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT'])
# @permission_classes((IsAuthenticated,))
# def get_or_edit_message(request, message_id):
#     user_message = Messages.objects.filter(user__username=request.user.username, id=message_id).values('id',
#                                                                                                        'user__username',
#                                                                                                        'text',
#                                                                                                        'date_sent').order_by(
#         'date_sent')
#     if not user_message:
#         return Response({"details": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
#     if request.method == 'GET':
#         return Response(user_message)
#     elif request.method == 'PUT':
#         user_message = Messages.objects.get(user__username=request.user.username, id=message_id)
#         serializer = MessageSerializer(user_message, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=CustomUserCreationSerializer,
    responses={
        '201': 'Created',
        '400': "Bad Request"
    },
    security=[],
    operation_id='auth_register_create',
    operation_description='This endpoint handles user registration'
)
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = CustomUserCreationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {
                "username": user.username,
                "email": user.email,
                'token': Token.objects.get(user=user).key
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageView(viewsets.ModelViewSet):
    """
    Get, Post, Update, Delete, Search and Filter your Anonymous Messages.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('text', 'likes', 'archives', 'ip_address')

    def get_queryset(self):
        if not self.request.user.pk:
            return None
        return Messages.objects.filter(user=self.request.user).order_by('-date_sent')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, device=self.request.META.get("HTTP_USER_AGENT", 'Unknown'),
                        ip_address=self.request.META.get("REMOTE_ADDR", 'Unknown'), )


class ArchiveMessageView(UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = (IsAuthenticated,)
    serializer_class = ArchiveLikeMessageSerializer
    lookup_field = 'id'

    def get_queryset(self):
        if not self.request.user.pk:
            return None
        return Messages.objects.filter(user=self.request.user).order_by('-date_sent')

    def perform_update(self, serializer):
        serializer.save(archived=True)


class UnArchiveMessageView(ArchiveMessageView):

    def perform_update(self, serializer):
        serializer.save(archived=False)


class LikeMessageView(ArchiveMessageView):

    def perform_update(self, serializer):
        serializer.save(liked=True)


class UnLikeMessageView(ArchiveMessageView):

    def perform_update(self, serializer):
        serializer.save(liked=False)


class PasswordResetView(APIView):
    """
    This sends password reset token to the user's email
    """

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        responses={
            '202': 'Accepted',
            '400': "Bad Request"
        },
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    """
    This confirms and the token and allows password reset if correct.
    """

    token_generator = default_token_generator
    user = None

    @swagger_auto_schema(
        request_body=SetPasswordSerializer,
        responses={
            '202': 'Accepted',
            '400': "Bad Request"
        },
    )
    def post(self, request, uidb64, token):
        try:
            self.user = self.get_user(uidb64)
        except UnboundLocalError:
            return Response({'error': 'invalid_link'}, status.HTTP_400_BAD_REQUEST)

        if self.user is not None:
            if self.token_generator.check_token(self.user, token):
                serializer = SetPasswordSerializer(data=self.request.data, user=self.user)
                if serializer.is_valid():
                    serializer.save()
                    data = {
                        'success': 'Password reset Complete',
                        'email': self.user.email
                    }
                    return Response(data, status=status.HTTP_202_ACCEPTED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'invalid_link'}, status.HTTP_401_UNAUTHORIZED)

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            UserModel = get_user_model()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user


class TelegramView(RetrieveUpdateAPIView):
    """
    Get, Post, Update, Delete, Search and Filter your Telegram details.
    """
    http_method_names = ['get', 'patch', ]
    permission_classes = (IsAuthenticated,)
    queryset = Telegram
    serializer_class = TelegramSerializer

    def get_object(self):
        obj = get_object_or_404(self.queryset, user=self.request.user)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj
