from functools import wraps

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages


def contact_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            body = "You must be logged in to view this page."
            messages.add_message(request, messages.ERROR, body)
            return HttpResponseRedirect(reverse('rapidsms.views.login'))
        if not request.contact:
            body = "You don't have access to this page (missing contact)."
            messages.add_message(request, messages.ERROR, body)
            return HttpResponseRedirect(reverse('rapidsms.views.login'))
        if not request.contact.site_id:
            body = "Associated contact record does not have a site."
            messages.add_message(request, messages.ERROR, body)
            return HttpResponseRedirect(reverse('rapidsms.views.login'))
        return func(request, *args, **kwargs)
    return wrapper
