""" Simple middleware to attach Contact to request object """

class ContactRequestMiddleware(object):
    def process_request(self, request):
        request.contact = None
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            try:
                request.contact = request.user.get_profile()
            except crm.Contact.DoesNotExist:
                pass
