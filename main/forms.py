from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Doctor,Patient
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Patient
from itertools import count
import uuid, random, string

# registration
class DoctorRegistrationForm(UserCreationForm):
    class Meta:
        model = Doctor
        fields = ('username', 'email', 'specialty','fullname','mobile','address','pincode')

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.doctor_id = f"{user.username.lower().replace(' ', '_')}_1"  # Assuming starting with _1
    #     if commit:
    #         user.save()
    #     return user

# Login
# class DoctorLoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.fields['username'].label = 'Username'
#             self.fields['password'].label = 'Password'

User = get_user_model()
class DoctorLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username/Mobile'
        self.fields['password'].label = 'Password'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                user = User.objects.get(Q(username=username) | Q(mobile=username))
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid login credentials.')

            if not user.check_password(password):
                raise forms.ValidationError('Invalid login credentials.')

            # Set the authentication backend
            self.user_cache = user
            self.user_cache.backend = 'main.backends.UsernameOrMobileModelBackend'

        return self.cleaned_data
    

def generate_random_patient_id(length=10):
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['patient_id','patient_name','diabetes_status','diabetes_type','left_image','right_image','patient_email']
        widgets = {
            'patient_id': forms.TextInput(attrs={'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-black dark:focus:ring-primary-500 dark:focus:border-primary-500'}),
            'patient_name': forms.TextInput(attrs={'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-black dark:focus:ring-primary-500 dark:focus:border-primary-500'}),
            'patient_email': forms.EmailInput(attrs={'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-black dark:focus:ring-primary-500 dark:focus:border-primary-500'}),
            'diabetes_status': forms.Select(choices=Patient.YES_NO_CHOICES, attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-black dark:focus:ring-primary-500 dark:focus:border-primary-500'}),
            'diabetes_type': forms.Select(choices=Patient.STAGE_CHOICES, attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-black dark:focus:ring-primary-500 dark:focus:border-primary-500'}),
        }

    def get_doctor_id(self):
        # Assuming you have access to the Doctor instance associated with the patient
        # You can replace this logic with how you associate a Doctor with a Patient in your system
        doctor_instance = Doctor.objects.get(username='suraj1')
        print(doctor_instance, 'OOOL')
        return doctor_instance.doctor_id

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            # Use the doctor_id in the patient_id field
            # self.fields['patient_id'].initial = f"{self.get_doctor_id()}-{get_next_id()}"
            # self.fields['patient_id'].initial = f"{str(uuid.uuid4())}"
            self.fields['patient_id'].initial = generate_random_patient_id()
            self.fields['patient_id'].widget.attrs['readonly'] = True

class CreditRequestForm(forms.Form):
    credit_value = forms.IntegerField(label='Enter the number of credits you want', required=True)
