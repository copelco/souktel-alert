#!/usr/bin/env python
# encoding=utf-8

from django.http import HttpResponse, HttpResponseRedirect

from groupmessaging.models import WebUser


def webuser_required(view):
    auth = WebUserAuthenticator(view)
    return auth.authenticate


class WebUserAuthenticator:
    def __init__(self, method):
        self.view = method

    def authenticate(self, request, *params, **kparams):
        self.request = request

        if '_auth_user_id' in request.session:
            try:
                user = WebUser.objects.get(id=request.session['_auth_user_id'])
            except WebUser.DoesNotExist:
                user = None
        else:
            user = None

        if user:
            commons = {'user': user}
            return self.view(request, commons, *params, **kparams)
        else:
            return HttpResponseRedirect('/accounts/login')
