from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect






class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        
        # We should do the recent url, as we have signup and login
        
        recent_url = request.GET.get('next')

        if recent_url:
            return recent_url

        # else fallback to signup
        
        return resolve_url('signup')
    def authentication_error(
    self,
    request,
    provider_id,
    error=None,
    exception=None,
    extra_context=None,
):
        return HttpResponseRedirect('/')