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

class TreesForm(forms.Form):
    trigger = forms.CharField(label=("Keyword"), max_length=50)
    root_state  = forms.ModelMultipleChoiceField(label=("First Question"), queryset=TreeState.objects.all())
    completion_text  = forms.CharField(label=("Completion Text"),max_length=30)

class QuestionForm(forms.Form):
    text = forms.CharField(label=("Message text"),widget=forms.Textarea(),
            initial=("Please enter your Question here"))
    error_response = forms.CharField(label=("Error text"),widget=forms.Textarea(),
            initial=("Please enter your Error Message here"))

    
