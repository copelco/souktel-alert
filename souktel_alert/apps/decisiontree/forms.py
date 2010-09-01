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

class QuestionForm(forms.Form):
    text = forms.CharField(label=("Message text"),widget=forms.Textarea(),
            initial=("Please enter your Question here"))
    error_response = forms.CharField(label=("Error text"),widget=forms.Textarea(),
            initial=("Please enter your Error Message here"))

    
