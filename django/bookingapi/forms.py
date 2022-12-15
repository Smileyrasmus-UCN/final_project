# forms.py

from django import forms
from .models import Constraints


class ConstraintsForm(forms.ModelForm):
    class Meta:
        model = Constraints
        fields = "__all__"
