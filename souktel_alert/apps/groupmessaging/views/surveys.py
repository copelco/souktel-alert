#!/usr/bin/env python
# encoding=utf-8
import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

from groupmessaging.views.common import webuser_required
from groupmessaging.models import *




@webuser_required
def list(request, context):
    ''' List all the Surveys'''
    surveys = Survey.objects.all()
    count = Survey.objects.count()
    mycontext = {'surveys': surveys, 'count': count}
    context.update(mycontext)
    return render_to_response('surveys_list.html', context,context_instance=RequestContext(request))

@webuser_required
def update(request, context, surveyid=None):
    '''form for Add/Edit surveys'''
    if not surveyid or int(surveyid) == 0:
        surv = None
    else:
        surv = Survey.objects.get(id=surveyid)

    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            if surv:

                surv.reference_code = form.cleaned_data['Reference Code']
                surv.reg_required = form.cleaned_data['Registration Required']
                surv.status = form.cleaned_data['Status']
                surv.title = form.cleaned_data['Title']
                surv.description = form.cleaned_data['Description']
                surv.site = context['user'].site
                surv.save()

            else:

                surv = Survey(reference_code=form.cleaned_data['Reference Code'],\
                                           reg_required=form.cleaned_data['Registration Required'],\
                                            status=form.cleaned_data['Status'],\
                                            site=context['user'].site)
                surv.save()
                surv = Message.objects.all()
                mycontext = {'surv': surv}
                context.update(mycontext)
                return redirect(list)

    else:
        if surv:
            data = {'reference code': surv.reference_code, 'reg required': surv.reg_required, 'status': surv.status}
        else:
            data = {'reference code': '', 'reg required': '', 'status': ''}
        form = SurveyForm(data)

    if not surveyid:
        surveyid = 0

    mycontext = {'surv': surv, 'form': form, 'surveyid': surveyid}
    context.update(mycontext)
    return render_to_response("survey_form.html", context, context_instance=RequestContext(request))


class SurveyForm(forms.Form):
    reference_code = forms.CharField(label=("Reference Code"), max_length=50)
    reg_required  = forms.BooleanField(label=("Registration Required"),required=True)
    Status = forms.BooleanField(label=("Status"),required=True)
    Title =  forms.CharField(label=("Title"), max_length=50)
    Description = forms.CharField(("Description"),widget=forms.Textarea())
    

