from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DiaryDetails, Diet


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class InfoForm(forms.ModelForm):
    class Meta:
        model = DiaryDetails
        fields = ["diary_name", "first_name", "last_name", "gender", "age", "weight"]


class DietForm(forms.ModelForm):
    class Meta:
        model = Diet
        fields = ["food_name", "Grams", "Energy", "Fat", "Carbohydrate", "Protein", "Fiber", "Sugars", "Sodium"]


class SearchFoodForm(forms.Form):
    search = forms.CharField(max_length=25, required=True)

    def get_text(self):
        return self.search

    def set_text(self, value):
        self.search = value




