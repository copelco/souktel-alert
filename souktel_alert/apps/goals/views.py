import datetime

from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.db.models import Count, Max
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from goals.models import Goal, Answer
from goals.forms import ScheduleForm, GoalFormSet

from group_messaging.decorators import contact_required


@contact_required
def summary(request):
    answers = Answer.objects.values('goal').annotate(count=Count('body'))
    try:
        answers = answers.order_by('-count')[0]['count']
    except IndexError:
        answers = 0
    goals = Goal.objects.order_by('-date_last_notified', '-date_created')
    if request.POST:
        form = ScheduleForm(request.POST)
        formset = GoalFormSet(request.POST, queryset=goals)
        if form.is_valid() and formset.is_valid():
            frequency = form.cleaned_data['frequency']
            start_date = form.cleaned_data['start_date']
            enabled_goals = formset.save(commit=False)
            now = datetime.datetime.now()
            for goal in enabled_goals:
                goal.schedule_start_date = start_date
                goal.schedule_repeat = frequency
                goal.save()
            messages.info(request, 'Schedule saved successfully')
            return HttpResponseRedirect(reverse('goal-summary'))
    else:
        form = ScheduleForm()
        formset = GoalFormSet(queryset=goals)

    context = {
        'goals': Goal.objects.order_by('-date_last_notified'),
        'total_answers': xrange(answers),
        'form': form,
        'formset': formset,
    }
    return render_to_response('goals/summary.html', context,
                              context_instance=RequestContext(request))
