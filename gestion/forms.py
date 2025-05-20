from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Client

class ClientRegisterForm(UserCreationForm):
    nom = forms.CharField(max_length=100)
    prenom = forms.CharField(max_length=100)
    email = forms.EmailField()
    tel = forms.CharField(max_length=20)
    adresse = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

