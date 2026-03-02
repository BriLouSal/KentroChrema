from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from .KOSAI import snaptrade_account_register





class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    # the mistake with snaptrade, we wanna ensure that the user email is not already authenticated with another account, and if it is, we wanna link the accounts together instead of creating a new one
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return
        try:
            existing_user = User.objects.get(email=email)
            if existing_user:
                sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass
    def get_login_redirect_url(self, request):
        user = request.user

        if not user.profile.snaptrade_user_id:
            snaptrade_account_register(user)

        return resolve_url('home')
    def authentication_error(
    self,
    request,
    provider_id,
    error=None,
    exception=None,
    extra_context=None,
):
        return HttpResponseRedirect('/')