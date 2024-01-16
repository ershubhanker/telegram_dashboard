from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'is_staff_member')


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

User = get_user_model()
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                user = User.objects.get(Q(username=username))
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid login credentials.')

            if not user.check_password(password):
                raise forms.ValidationError('Invalid login credentials.')

            # Set the authentication backend
            self.user_cache = user
            self.user_cache.backend = 'main.backends.UsernameOrMobileModelBackend'

        return self.cleaned_data