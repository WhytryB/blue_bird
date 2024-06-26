from datetime import timedelta

from django import forms
from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,  PasswordChangeForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
User = get_user_model()



class UserCacheMixin:
    user_cache = None


class SignIn(UserCacheMixin, forms.Form):
    password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean_password(self):
        password = self.cleaned_data['password']

        if not self.user_cache:
            return password

        if not self.user_cache.check_password(password):
            raise ValidationError(_('You entered an invalid password.'))

        return password




class SignInViaUsernameForm(SignIn):
    username = forms.CharField(
    widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'padding-left: 20px !important;', 'autocomplete': 'username'}),
    label=_('Username'))

    @property
    def field_order(self):
        return ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']
        code = self.data.get('country_code').replace("+", "")
        phone = code + username
        user = User.objects.filter(username=phone).first()
        if not user:
            raise ValidationError(_('You entered an invalid username.'))

        if not user.is_active:
            raise ValidationError(_('This account is not active.'))

        self.user_cache = user

        return phone


class ChangeProfileForm(forms.Form):
    first_name = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ім'я"}), max_length=30, required=False)
    last_name = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Прізвище"}), max_length=30, required=False)
    middle_name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "По батькові"}),
            max_length=30,
            required=False
        )
    mobile = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Мобільний"}),
            max_length=15,
            required=False
        )
    email = forms.EmailField(
            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Електронна пошта"}),
            max_length=254,
            required=False
        )
    address = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Адреса"}),
            required=False
        )
    profile_picture = forms.ImageField(
            widget=forms.FileInput(attrs={'class': 'form-control'}),
            required=False
        )
    old_password = forms.CharField(
        label='Старий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Поточний Пароль", 'autocomplete': 'off'}),
        required=False,
    )
    new_password = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Пароль", 'autocomplete': 'off'}),
        required=False,
    )


class ChangePasswordPhoneForm(forms.Form):
    phone = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Номер телефону"}), max_length=14, required=True)


class ChangePasswordCodeForm(forms.Form):
    reset_code = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Код підтвердження"}), max_length=6, required=True)


class ChangePasswordConfirmForm(forms.Form):
    new_password = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Новий пароль"}), min_length=5, max_length=25, required=True)
    confirm_password = forms.CharField( widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Підтвердити пароль"}), min_length=5, max_length=25, required=True)