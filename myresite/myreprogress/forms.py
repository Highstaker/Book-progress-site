from django import forms
from django.core.validators import MinValueValidator


class PageInsertForm(forms.Form):
	insert_at = forms.IntegerField(label="Insert at position", validators=(MinValueValidator(1),), min_value=1,
								   widget=forms.NumberInput(attrs={"autocomplete": "off"})
								   )
	amount = forms.IntegerField(label="Amount of pages", validators=(MinValueValidator(1),), min_value=1,
								widget=forms.NumberInput(attrs={'value': 1, "autocomplete": "off"})  # default value
								)
