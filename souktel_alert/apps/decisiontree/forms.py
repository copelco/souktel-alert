#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from models import *

class TreeForm(forms.ModelForm):
	class Meta:
		model = Tree

	def clean_alias(self):
		data = self.cleaned_data["trigger"]
		return data.lower()

class AnswerForm(forms.ModelForm):
	class Meta:
		model = Answer 

	def clean_alias(self):
		data = self.cleaned_data["trigger"]
		return data.lower()

class TreesForm(forms.ModelForm):

    class Meta:
        model = Tree

    def __init__(self, *args, **kwargs):
        super(TreesForm, self).__init__(*args, **kwargs)
        self.fields['trigger'].label = 'Keyword'
        self.fields['root_state'].label = 'First Question'
        self.fields['completion_text'].label = 'Completion Text'

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = 'Message Text'
        self.fields['error_response'].label = 'Error Text'
    
    
class StateForm(forms.ModelForm):

    class Meta:
        model = TreeState

    def __init__(self, *args, **kwargs):
        super(StateForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'name'
        self.fields['question'].label = 'question'
        self.fields['num_retries'].label = 'num retries'

class ReportForm(forms.Form):
    ANALYSIS_TYPES = (
        ('A', 'Mean'),
        ('R', 'Median'),
        ('C', 'Mode'),
    )
    answer    = forms.CharField(label=("answer"),required=False)
    dataanalysis = forms.ChoiceField(choices=ANALYSIS_TYPES)


class AnswerSearchForm(forms.Form):
    answer = forms.ModelChoiceField(queryset=Answer.objects.none())

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree
        super(AnswerSearchForm, self).__init__(*args, **kwargs)
        answers = \
            Answer.objects.filter(transitions__entries__session__tree=tree)
        self.fields['answer'].queryset = answers.distinct()


class EntryTagForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ('tags',)


class PathForm(forms.ModelForm):

    class Meta:
        model = Transition

    def __init__(self, *args, **kwargs):
        super(PathForm, self).__init__(*args, **kwargs)
        self.fields['current_state'].label = 'Current State'
        self.fields['answer'].label = 'Answer'
        self.fields['next_state'].label = 'Next State'