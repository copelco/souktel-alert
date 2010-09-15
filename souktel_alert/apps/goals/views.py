from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.db.models import Count, Max

from goals.models import Goal, Answer

from group_messaging.decorators import contact_required


@contact_required
def summary(request):
    answers = Answer.objects.values('goal').annotate(count=Count('body'))
    try:
        answers = answers.order_by('-count')[0]['count']
    except IndexError:
        answers = 0
    context = {
        'goals': Goal.objects.order_by('-date_last_notified'),
        'total_answers': xrange(answers),
    }
    return render_to_response('goals/summary.html', context,
                              context_instance=RequestContext(request))
