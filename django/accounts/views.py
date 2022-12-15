from rest_framework import viewsets

from django.contrib.auth.models import Group
from .models import CustomUser
from .serializers import UserSerializer, GroupSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render


from rest_framework.permissions import IsAuthenticated

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = CustomUser.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # auto create token on user creation
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)

    # @action(detail=False, methods=["get", "post"], url_path="account-form")
    # def account_form(self, request):
    #     if request.method == "GET":
    #         return render(
    #             request,
    #             "account_form.html",
    #             {"user": request.user, "conditions": request.user.conditions},
    #         )
    #     if request.method == "POST":
    #         for item in request.POST:
    #             if item == "csrfmiddlewaretoken":
    #                 continue
    #             if request.POST[item] == "true":
    #                 bool = True
    #             if request.POST[item] == "false":
    #                 bool = False
    #             for key, value in request.user.conditions.items():
    #                 if item in value:
    #                     request.user.conditions[key][item] = bool
    #                     request.user.save()

    #         return Response(
    #             {
    #                 "message": "Success!",
    #                 "usercond": request.user.conditions,
    #             }
    #         )


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
