from django import forms
from django.core.validators import MinValueValidator


class PageInsertForm(forms.Form):
	insert_at = forms.IntegerField(label="Insert at position", validators=(MinValueValidator(1),))
	amount = forms.IntegerField(label="Amount of pages", validators=(MinValueValidator(1),))