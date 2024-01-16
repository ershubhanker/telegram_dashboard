from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse
from main.forms import DoctorRegistrationForm
from django.contrib.sites.models import Site
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer

from django.core.mail import EmailMessage
from django.utils import timezone

from django.shortcuts import render, HttpResponse
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import DoctorRegistrationForm, DoctorLoginForm
from django.contrib.auth import authenticate, get_user_model
from .backends import UsernameOrMobileModelBackend
from django.contrib import messages
from .forms import PatientForm, CreditRequestForm
import requests
import json
import os
import random
import string
from reportlab.platypus import KeepTogether
import pandas as pd
from django.template.loader import get_template
from .models import Patient, Doctor, CreditRequest, EmailToken
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.lib.colors import white, HexColor, black, green
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime, timedelta
from reportlab.lib import colors
from datetime import datetime, date
from django.db.models import Q
from django.http import JsonResponse
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from .serializer import *
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView ,InvalidToken
from rest_framework.permissions import IsAuthenticated
from django.views import View
from .email import Sendresetpasswordlink
import uuid
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay

global_token=None
check_user=None
def save_token(token_value, user):
    # Declare the global variable inside the function to indicate you're modifying the global variable
    global global_token
    global check_user
    global_token = token_value
    check_user=user

    print(f"Token value '{token_value}' saved successfully. y user{check_user}")

def get_saved_token():
    # Access the global variable
    global global_token
    global check_user
    print(global_token, check_user)
    return global_token, check_user

# register
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'main.UsernameOrMobileModelBackend'
            login(request, user)
            return redirect('doctor_login')  # Change to your desired redirect URL
        else:
            # Display error messages for form validation errors
            error_messages = ', '.join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            messages.error(request, f"Registration failed. {error_messages}")
    else:
        form = DoctorRegistrationForm()
    return render(request, 'register.html', {'form': form})

class Resetpasswordview(View):
    def get(self, request):
        return render(request, "forget_password.html")

    def post(self,request):
        email = request.POST.get("email")

        user = Doctor.objects.filter(email=email.lower()).first()

        if user:
            token = uuid.uuid4()
            obj, _ = EmailToken.objects.get_or_create(user=user)
            obj.email_token = token
            obj.save()
            receiver_email = obj.user.email
            Sendresetpasswordlink(receiver_email,obj.email_token )
            messages.success(request,f"The link to reset your password has been emailed to: {receiver_email}")
            return render(request, 'forget_password.html')
        
        messages.error(request,f"User does not exist")
        return render(request, 'forget_password.html')

    
class confirmpassword(View):
    def get(self, request, token=None):
        try:
            token_obj = EmailToken.objects.filter(email_token=token).first()

            return render(request, "forget_confirm.html",{'token':token_obj.email_token})
        
        except Exception as e:
            messages.error(request,f"Invaild or expired URL")
            return render(request, 'forget_password.html')
            # return HttpResponse("invaild url")

    def post(self, request,token=None):

        password = request.POST.get("password1")
        print(token, 'SAKAL')
        obj  = EmailToken.objects.filter(email_token= token).first()
        print(obj.user.email, 'OOOOOOP',obj.user.id)
        user_obj = Doctor.objects.filter(id=obj.user_id).first()
        print()
        try:
            user_obj = Doctor.objects.filter(id=obj.user.id).first()
            print(user_obj,'okok')
            user_obj.set_password(password)
            user_obj.save()
            obj.delete()
            messages.success(request,f"Password updated successfully")
            # return HttpResponse("Passoword  Update  successfully")
            return render(request, "login.html",{'token':token})
        except Exception as e:
            messages.error(request,f"User does not exist")
            print(e, 'SAJAL @')
            return render(request, "forget_password.html",{'token':token})
        

def email_verification_sent(request):
    return render(request, 'email_verification_sent.html')

# def doctor_register(request):
#     if request.method == 'POST':
#         form = DoctorRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.backend = 'main.UsernameOrMobileModelBackend'
            
#             # Generate a verification token and create a verification URL
#             # token = default_token_generator.make_token(user)
#             # uid = urlsafe_base64_encode(force_bytes(user.pk))
#             # current_site = get_current_site(request)
#             # verification_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})

#             # Generate a verification token and create a verification URL
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             current_site = Site.objects.get_current()
#             verification_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})


#             print("uid:", uid)
#             print("token:", token)



            
#             # Build the email subject and message
#             subject = 'Verify your email address'
#             message = render_to_string('email_verification_message.txt', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'verification_url': verification_url,
#             })
#             # message="hello"
#             # Send the verification email
#             send_mail(subject, message, 'boredstuff2021@gmail.com', [user.email])
            
#             # Redirect to a page indicating that an email has been sent for verification
#             return redirect('email_verification_sent.html')
#         else:
#             # Display error messages for form validation errors
#             error_messages = ', '.join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
#             messages.error(request, f"Registration failed. {error_messages}")
#     else:
#         form = DoctorRegistrationForm()
#     return render(request, 'register.html', {'form': form})

# login
def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                credit_requset_list(request)
                return redirect('admin_home')  # Redirect to staff-specific page
            else:
                return redirect('index')  # Redirect to regular home page
        else:
            messages.error(request, 'Invalid Username or Password. Please try again.')
    else:
        form = DoctorLoginForm()
    return render(request, 'login.html', {'form': form})


# logout
def doctor_logout(request):
    logout(request)
    return redirect('doctor_login') 

# home page
def home(request):
    return render(request, 'home.html')

# send credit requset data to admin home
from django.core import serializers

def credit_requset_list(request):
    # if request.method == 'GET':
    request_list = CreditRequest.objects.all()
    serialized_data = serializers.serialize('json', request_list)
    print('serialized_data',serialized_data)
    # h={'shvjh':'hvxhg'}
    return JsonResponse(serialized_data, safe=False)
# def credit_request_list(request):
#     request_list = CreditRequest.objects.all()
#     serialized_data = []

#     for credit_request in request_list:
#         serialized_request = {
#             'doctor_name': credit_request.doctor.fullname,
#             'request_date': credit_request.request_date,
#             'credit_value': credit_request.credit_value,
#         }
#         serialized_data.append(serialized_request)

#     return JsonResponse(serialized_data, safe=False)


# Define a function to get the number of patients for each weekday
def patients_by_weekday():
    return (
        Patient.objects
        .values('timestamp__week_day')  # Extract the day of the week
        .annotate(patient_count=Count('id'))  # Count the number of patients for each weekday
        .order_by('timestamp__week_day')
        .values_list('patient_count', flat=True)  # Optional: order the results by weekday
    )
# admin home page
def adminhome(request):
    return render(request, 'admin_index.html')
    # return render(request, 'admin_home.html')

# dashboard (doctor)
def index(request):
    # # Fetch all patient objects from the database
    # # patients = Patient.objects.all()
    
    # doctor_admitted_patients = Patient.objects.filter(doctor_id=request.user.id)
    # total_patients = doctor_admitted_patients.count()
    # print(total_patients,"Total patients", request.user.id)
    # patients_by_day = list(patients_by_weekday())
    # print(patients_by_day, )

    # # Patient today 
    # start_of_day = datetime.combine(date.today(), datetime.min.time())
    # end_of_day = datetime.combine(date.today(), datetime.max.time())

    # # Filter patients whose timestamp is within the current day
    # # today_patients = Patient.objects.filter(patient_id=request.user.id)
    # # today_patients = Patient.objects.filter(timestamp__range=(start_of_day, end_of_day))
    # today_patients = Patient.objects.filter(Q(patient_id=request.user.id) & Q(timestamp__range=(start_of_day, end_of_day)))
    # today_patients = today_patients.count()
    # print(today_patients,"today_patients", request.user.id)

    # # Calculate the start and end of the current month
    # start_of_month = datetime(date.today().year, date.today().month, 1)
    # end_of_month = datetime(date.today().year, date.today().month, date.today().day, 23, 59, 59)
    
    # # Filter patients whose timestamp is within the current month
    # patients_this_month = Patient.objects.filter(timestamp__range=(start_of_month, end_of_month))
    # patients_this_month = Patient.objects.filter(Q(patient_id=request.user.id) & Q(timestamp__range=(start_of_month, end_of_month)))
    # patients_this_month=patients_this_month.count()
    # print('patients_this_month',patients_this_month)

    # #get details of all patients
    # # patients = Patient.objects.all()
    # patients = Patient.objects.filter(doctor_id=request.user.id)
    # patient_info = []

    # for p in patients:
    #     patient_info.append({
    #         'name':p.patient_name,
    #         'diabetes_status':p.diabetes_status,
    #         'diabetes_type':p.diabetes_type,
    #         'patient_email':p.patient_email,
    #         'appointed_doctor':p.doctor,
    #         }
    #     )
    # context={'total_patients': total_patients, 
    #         'today_patients': today_patients,
    #         'patients_this_month': patients_this_month,
    #         'patient_info':patient_info,
    #         'patients_by_day':patients_by_day
    #         }

    return render(request, 'index.html')

def DoctorProfile(request):
    doctor = Doctor.objects.get(id=request.user.id)
    print(doctor, 'Profile')
    context={'doctor':doctor}
    return render(request, 'doctorpanel/doctor-profile.html', context)

# services (doctor)
def services(request):
    return render(request,'doctorpanel/services.html')

# upload Image (doctor)
# d = pd.read_csv("D:/maskottchen/zia-project/zia_project/dristieye/main/icd_codes.csv")
# d = pd.read_csv("C:/Users/user/Desktop/Django_project/zia_project/dristieye/main/icd_codes.csv")
# Get the base directory of your Django project
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)) ) # Assuming this script is in the same folder as manage.py

# Construct the path to the CSV file in the "main" app directory
csv_file_path = os.path.join(base_dir, 'main', 'icd_codes.csv')
# Read the CSV file into a DataFrame
d = pd.read_csv(csv_file_path)

def uploadImages(request):
    api_responses = {
        "left_eye": {},
        "right_eye": {},
    }

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)     # Enabling forms to accept the file submitted by the user
        
        if form.is_valid():

            current_user = request.user  # Get the currently logged-in doctor.
            print(request.user.id)
            
            user_credit = Doctor.get_credit(current_user)  # Get the doctor's credit.
            print(user_credit, "USER CREDIT", current_user)
            

            # Check if the user has enough credit to deduct
            if user_credit > 0:
                patient_id = form.cleaned_data['patient_id']
                patient_name = form.cleaned_data['patient_name']
                diabetes_status = form.cleaned_data['diabetes_status']
                diabetes_type = form.cleaned_data['diabetes_type']
                ss =  form.cleaned_data['left_image']
                rr=  form.cleaned_data['right_image']
                # print(ss,rr)
                
                patient = form.save(commit=False)

                patient.doctor = request.user

                # print("------------------------",type(patient_id))
                
                patient.save()
                
                left_quality,left_analyze,right_quality,right_analyze = 0.0,0.0,0.0,0.0
                try:
                    val = Patient.objects.get(patient_id=patient_id)
                    print(val, 'VAl')
                except:
                    return render(request, 'same_id_error.html')
                    
                print(val.left_image, val.right_image)
        
                # Condition for left image
                if val.left_image:
                    left_api_url = f'http://3.7.242.24:8006/quality_check?unique_id={patient_id}'
                    left_files = {'file': open(f"{val.left_image}", 'rb')}
                    left_response = requests.post(left_api_url, files=left_files)
                    api_responses["left_eye"]["quality_check"] = left_response.json()
                    # left_quality = float(left_response.json().get("model_coef"))  #should be used for comparison
                    try:
                        left_quality = float(left_response.json().get("model_coef"))
                    except ValueError:
                        # Handle the case when the value is 'NA' or not a valid float
                        left_quality = None


                    left_api_analyze_url = f'http://3.7.242.24:8000/dr_analyze?unique_id={patient_id}'
                    left_analyze_files = {'file': open(f"{val.left_image}", 'rb')}
                    left_analyze_response = requests.post(left_api_analyze_url, files=left_analyze_files)
                    print(left_analyze_response, 'left_analyze_response CHECK')
                    print(left_analyze_response.json(), 'left_analyze_response JSON')
                    left_analyze_data = left_analyze_response.json()
                    
                    left_model_response = left_analyze_data["model_response"]
                    try:
                        left_analyze = float(left_analyze_response.json().get("model_coef"))         #should be used to compare with left_dr
                    
                    except:
                        left_analyze = None
                    left_binary_response = left_analyze_data["binary_response"]

                # Condition for right image
                if val.right_image:
                    right_api_url = f'http://3.7.242.24:8006/quality_check?unique_id={int(patient_id)+1}'
                    right_files = {'file': open(f"{val.right_image}", 'rb')}
                    right_response = requests.post(right_api_url, files=right_files)
                    api_responses["right_eye"]["quality_check"] = right_response.json()
                    right_quality = float(right_response.json().get("model_coef"))     #should be used in comparison

                    right_api_analyze_url = f'http://3.7.242.24:8000/dr_analyze?unique_id={int(patient_id)+1}'
                    right_analyze_files = {'file': open(f"{val.right_image}", 'rb')}
                    right_analyze_response = requests.post(right_api_analyze_url, files=right_analyze_files)
                    right_analyze_data = right_analyze_response.json()

                    right_model_response = right_analyze_data["model_response"]
                    right_analyze = float(right_analyze_response.json().get("model_coef"))             #compared with the right_dr
                    right_binary_response = right_analyze_data["binary_response"]

                report_data = {
                    'patient_id': patient_id,
                    'patient_name': patient_name,
                    'diabetes_status': diabetes_status,
                    'diabetes_type': diabetes_type,
                    'username': request.user.username,
                }

                # Handle the case where only a single image is uploaded
                if val.left_image and not val.right_image:
                    report_data['left_model_response'] = left_model_response
                    report_data['left_model_coef'] = left_analyze
                    report_data['left_binary_response'] = left_binary_response
                    report_data['left_quality'] = left_quality
                    report_data['left_eye_image_path'] = f"{val.left_image}"
                    # print("for left")
                    # print(report_data['left_eye_image_path'])
                    report_data['right_eye_image_path'] = ""
                elif val.right_image and not val.left_image:
                    report_data['right_model_response'] = right_model_response
                    report_data['right_model_coef'] = right_analyze
                    report_data['right_binary_response'] = right_binary_response
                    report_data['right_quality'] = right_quality
                    report_data['right_eye_image_path'] = f"{val.right_image}"
                    report_data['left_eye_image_path'] = ""
                else:
                    report_data['left_model_response'] = left_model_response
                    report_data['left_model_coef'] = left_analyze
                    report_data['left_binary_response'] = left_binary_response
                    report_data['left_quality'] = left_quality
                    report_data['left_eye_image_path'] = f"{val.left_image}"
                    report_data['right_model_response'] = right_model_response
                    report_data['right_model_coef'] = right_analyze
                    report_data['right_binary_response'] = right_binary_response
                    report_data['right_quality'] = right_quality
                    report_data['right_eye_image_path'] = f"{val.right_image}"
                    print("for BOTH")
                    print(report_data['left_eye_image_path'])
                    print(report_data['right_eye_image_path'])
                
                #fetching data from ICD CODES
                filtered_rows = d[
                    (d['right_dr'] == right_analyze) &
                    (d['right_dme'] == right_quality) &
                    (d['left_dr'] == left_analyze) &
                    (d['left_dme'] == left_quality)
                    ]
                
                summary = ''
                icd_codes = ''
                icd_desc = ''
                left_result = ''
                right_result = ''

                for index, row in filtered_rows.iterrows():
                    summary = row['summary']
                    icd_codes = row['icd_codes']
                    icd_desc = row['icd_desc']
                    left_result = row['left_result']
                    right_result = row['right_result']
                report_data['summary'] = summary
                report_data['icd_codes'] = icd_codes
                report_data['icd_desc'] = icd_desc
                report_data['left_result'] = left_result
                report_data['right_result'] = right_result

                # Redirect to generate_report view with API responses
                print(report_data, "REPORTS DETAILS")
                try:
                    result= generate_report(request,api_responses, report_data)
                    print(result.status_code, 'RESULT')
                    if result.status_code==200:
                        current_user.remove_credit() 
                        print('AFTER DELETE', current_user.credit_val)
                    return result
                except Exception as e:
                    print('ERROR WHILE CREATING REPORT', e)
                    val.delete()
                    return render(request, 'mail_error.html')
            else:
                # User has zero credit, display a message
                return render(request, 'doctorpanel/recharge.html')

    else:
        form = PatientForm()
    return render(request,'doctorpanel/uploadImage.html',{'form': form})



class GetJwtToken(APIView):
    global check_token
    permission_classes = ()
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # print(username, password, 'fafaf')
        # user = authenticate(request=request, email=email, password=password)
        user = authenticate(username=username, password=password)
        print(user, 'user')
        if user:
            serializer = LoginSerializer(
                data=request.data, context={"request": request}
            )
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                raise InvalidToken(e.args[0])
            print(serializer.validated_data['access'], 'TESTING TOKEN')
            save_token(serializer.validated_data['access'], user)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(
            {"message": "Invalid data"}, status=status.HTTP_401_UNAUTHORIZED
        )


def generate_random_patient_id(length=10):
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# def generate_random_patient_id(length=10):
#     return ''.join((random.randint(0, 9)) for _ in range(length))

class  ImageprocessViewAPI(ModelViewSet):
    global token_value
    serializer_class = UploadImgeSerializer
    queryset = ""

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
    
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name')
        email = serializer.validated_data.get('email')
        diabetes_status = serializer.validated_data.get('diabetes_status')
        diabetes_type = serializer.validated_data.get('diabetes_type')
        left_eye = serializer.validated_data.get('left_eye')
        right_eye = serializer.validated_data.get('right_eye')
        token = serializer.validated_data.get('check_token')
        # print(get_saved_token, 'GOTIT')
        second_value, current_user=get_saved_token()
        print(second_value, 'GOTIT', current_user)
        user_credit = Doctor.get_credit(current_user)  # Get the doctor's credit.
        print(user_credit, "USER CREDIT", current_user)
        if token==second_value:
            
            patient_id=generate_random_patient_id()
            # print(left_eye)
            # print(type(left_eye))

            api_responses = {
            "left_eye": {},
            "right_eye": {},}
            left_quality,left_analyze,right_quality,right_analyze = 0.0,0.0,0.0,0.0
            if left_eye is None and right_eye is None:
                
                return Response(
                {"message": "No single images found"})

            if left_eye:
                left_api_url = f'http://3.7.242.24:8006/quality_check?unique_id={patient_id}'
                # left_files = {'file': open(f"{left_eye}", 'rb')}
                left_files = {'file': left_eye}
                left_response = requests.post(left_api_url, files=left_files)
                print(left_response.json(), 'JSON')
                print(left_response.json().get("model_coef"), 'JSONlp')
                api_responses["left_eye"]["quality_check"] = left_response.json()
                try:
                    left_quality = float(left_response.json().get("model_coef"))
                    # print(left_quality,'TEST')
                except ValueError:
                    left_quality = 0.0

                left_api_analyze_url = f'http://3.7.242.24:8000/dr_analyze?unique_id={patient_id}'
                # left_analyze_files = {'file': open(f"{left_eye}", 'rb')}
                left_analyze_files = {'file': left_eye}
                left_analyze_response = requests.post(left_api_analyze_url, files=left_analyze_files)
                left_analyze_data = left_analyze_response.json()

                left_model_response = left_analyze_data["model_response"]
                try:
                    left_analyze = float(left_analyze_response.json().get("model_coef"))
                except ValueError:
                    left_analyze=0.0
                left_binary_response = left_analyze_data["binary_response"]

            if right_eye:
                right_api_url = f'http://3.7.242.24:8006/quality_check?unique_id={int(patient_id) + 1}'
                right_files = {'file': right_eye}
                right_response = requests.post(right_api_url, files=right_files)
                api_responses["right_eye"]["quality_check"] = right_response.json()
                right_quality = float(right_response.json().get("model_coef"))

                right_api_analyze_url = f'http://3.7.242.24:8000/dr_analyze?unique_id={int(patient_id) + 1}'
                right_analyze_files = {'file':right_eye}
                right_analyze_response = requests.post(right_api_analyze_url, files=right_analyze_files)
                right_analyze_data = right_analyze_response.json()

                right_model_response = right_analyze_data["model_response"]
                try:
                    right_analyze = float(right_analyze_response.json().get("model_coef"))
                except:
                    right_analyze=0.0
                right_binary_response = right_analyze_data["binary_response"]

            report_data = {
                'patient_id': patient_id,
                'patient_name': name,
                'diabetes_status': diabetes_status,
                'diabetes_type': diabetes_type,
                # 'username': request.user.username,
            }

            if left_eye and not right_eye:
                report_data['left_model_response'] = left_model_response
                report_data['left_model_coef'] = left_analyze
                report_data['left_binary_response'] = left_binary_response
                report_data['left_quality'] = left_quality
                # report_data['left_eye_image_path'] = left_eye
                # report_data['right_eye_image_path'] = ""
            elif right_eye and not left_eye:
                report_data['right_model_response'] = right_model_response
                report_data['right_model_coef'] = right_analyze
                report_data['right_binary_response'] = right_binary_response
                report_data['right_quality'] = right_quality
                # report_data['right_eye_image_path'] = right_eye
                # report_data['left_eye_image_path'] = ""
            else:
                report_data['left_model_response'] = left_model_response
                report_data['left_model_coef'] = left_analyze
                report_data['left_binary_response'] = left_binary_response
                report_data['left_quality'] = left_quality
                # report_data['left_eye_image_path'] = left_eye
                report_data['right_model_response'] = right_model_response
                report_data['right_model_coef'] = right_analyze
                report_data['right_binary_response'] = right_binary_response
                report_data['right_quality'] = right_quality
                # report_data['right_eye_image_path'] = right_eye

            # Rest of your code for generating reports
            #fetching data from ICD CODES
            # d = pd.read_csv(csv_file_path)
            # print(left_quality,left_analyze,right_quality,right_analyze)
            # print(d)
            filtered_rows = d[
                (d['right_dr'] == right_analyze) &
                (d['right_dme'] == right_quality) &
                (d['left_dr'] == left_analyze) &
                (d['left_dme'] == left_quality)
                ]
            
            summary = ''
            icd_codes = ''
            icd_desc = ''
            left_result = ''
            right_result = ''
            # print(filtered_rows, 'filtered_rows')

            for index, row in filtered_rows.iterrows():
                summary = row['summary']
                icd_codes = row['icd_codes']
                icd_desc = row['icd_desc']
                left_result = row['left_result']
                right_result = row['right_result']
            report_data['summary'] = summary
            report_data['icd_codes'] = icd_codes
            report_data['icd_desc'] = icd_desc
            report_data['left_result'] = left_result
            report_data['right_result'] = right_result

            print(report_data,'kll')
            if user_credit>0:
                current_user.remove_credit() 
                print('AFTER API USED CREDIT', current_user.credit_val)
                # return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return render(request, 'doctorpanel/recharge.html')
            return Response(report_data)
        else:
            return Response(
            {"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )

#API TO REPORT DATAfrom django.http import JsonResponse

# reportgenerator
def generate_report(request, api_responses,report_data):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    

    # doc = SimpleDocTemplate(response, pagesize=letter)
    # story = []

    # styles = getSampleStyleSheet()
    # report_title = Paragraph("Eye Report", styles['Title'])
    # story.append(report_title)
    # story.append(Spacer(1, 20))

    # # Get the template and render it
    # template = get_template('doctorpanel/report_template.html')
    # context = {
    #     'api_responses': api_responses,
    #     'report_data': report_data,
    # }
    # rendered_template = template.render(context)
    
    # # Convert the HTML content to ReportLab elements
    # story.append(KeepTogether(Paragraph(rendered_template, styles['Normal'])))

    # doc.build(story)
    c = canvas.Canvas(response, pagesize=letter)
    styles = getSampleStyleSheet()
        # Load the logo image
    logo_path = "static/images/report_logo.png"
    logo = ImageReader(logo_path)
    # Draw a white rectangle as the background of the logo
    c.setFillColor(white)
    c.rect(0.5*inch, letter[1] - 0.5*inch, 3*inch, 0.5*inch, fill=True, stroke=False)
    # Draw the logo over the white rectangle (adjust dimensions as needed)
    c.drawImage(logo,0.5*inch, letter[1] - 0.8*inch, width=3*inch, height=0.5*inch)
    # Add your content here using the canvas.drawString(), canvas.drawParagraph(), etc.
    #writing Headings
    # Add text under the logo
    text = "Eye Screen Service"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(black)
    c.drawString(0.5*inch, letter[1] - 1.3*inch, text)
    second_line_text = "Diabetic Retinopathy Screening Report"
    c.setFont("Helvetica", 12)
    c.drawString(0.5*inch, letter[1] - 1.6*inch, second_line_text)


    #Drawing Line
    c.setStrokeColor(HexColor("#208295"))  # Use a blue color for the line
    c.setLineWidth(2)  # Set a thinner line width
    c.line(0.5*inch, letter[1] - 1.8*inch, 8*inch, letter[1] - 1.8*inch)

    #***Line below Box***
    c.setStrokeColor(HexColor("#208295"))  # Use a blue color for the line
    c.setLineWidth(17) 
    c.line(0.5*inch, letter[1] - 3.3*inch, 8*inch, letter[1] - 3.3*inch) # line used for heading fundus images used in examination

    #creatingbox
    box_width = 7.5*inch
    box_height = 1*inch
    box_x = 0.5*inch
    box_y = letter[1] - 3.0*inch
    box_border_width = 1


    c.setStrokeColor(HexColor("#000000"))  # Black color for the border
    c.setLineWidth(box_border_width)
    c.rect(box_x, box_y, box_width, box_height, fill=False, stroke=True)

    #Patient details
    patient_mrn = report_data['patient_id']
    current_datetime = datetime.now()
    imaging_datetime = current_datetime.strftime('%a %d %b %H:%M:%S %Y')
    patient_name = report_data['patient_name']
    report_datetime = current_datetime.strftime('%a %d %b %H:%M:%S %Y')
    doctor_name = report_data['username']

    # Add fields inside the box
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(black)
    field_x_left = box_x + 10
    field_x_right = box_x + box_width - 250
    field_y = box_y + 10

    c.drawString(field_x_left, field_y + 40, f"Patient MRN: {patient_mrn}")
    c.drawString(field_x_right - 30, field_y + 40, f"Imaging Date-Time: {imaging_datetime}")

    c.drawString(field_x_left, field_y + 20, f"Patient Name: {patient_name}")
    c.drawString(field_x_right - 30, field_y + 20, f"Report Date-Time: {report_datetime}")

    c.drawString(field_x_left, field_y + 1, f"Doctor Name: {doctor_name}")

    #************Reports Start************

    text = "FUNDUS IMAGES USED IN EXAMINATION"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(white)
    c.drawCentredString(4.3*inch, letter[1] - 3.4*inch, text)

    #Box for generating Images

    box_width = 7.5*inch
    box_height = 3.77*inch
    box_x = 0.5*inch
    box_y = letter[1] - 7.2*inch
    box_border_width = 1


    c.setStrokeColor(HexColor("#000000"))  # Black color for the border
    c.setLineWidth(box_border_width)
    c.rect(box_x, box_y, box_width, box_height, fill=False, stroke=True)
    
    # Load the two images
    image1_path = report_data.get('left_eye_image_path', '')
    image2_path = report_data.get('right_eye_image_path', '')
    # print(image1_path)
    # print(image2_path)
    # print(report_data)


    image1 = None
    image2 = None
    

    if image1_path:
        image1 = ImageReader(image1_path)

    if image2_path:
        image2 = ImageReader(image2_path)

    # Calculate image positions and dimensions
    image_width = 2.0*inch
    image_height = 2.0*inch
    image1_x = 1.1*inch
    image_y = letter[1] - 6.3*inch
    image2_x = image1_x + image_width + 0.5*inch

    # Draw the images on the canvas
    if image1:
        c.drawImage(image1, image1_x, image_y, width=image_width, height=image_height)

    if image2:
        c.drawImage(image2, image2_x + 20, image_y, width=image_width, height=image_height)

    #*************ICD codes text**************
    #ICD codes fetching
    left_eye_icd = report_data['left_result']
    right_eye_icd = report_data['right_result']
    #Left Image
    if image1:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(green)
        c.drawCentredString(2.5*inch, letter[1] - 6.6*inch, f"OS(LE): {left_eye_icd}")

    #Right Image ICD code
    if image2:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(green)
        c.drawCentredString(6.2*inch, letter[1] - 6.6*inch, f"OS(RE): {right_eye_icd}")

    #conditional line
    text = "*Image orientation and labeling is for reference purpose only and should not be used for diagnostic purpose"
    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    c.drawString(0.8*inch, letter[1] - 7*inch, text)

    #*********Diagnosis***********
    #creating a label for heading
    c.setStrokeColor(HexColor("#208295"))  # Use a blue color for the line
    c.setLineWidth(17) 
    c.line(0.5*inch, letter[1] - 7.5*inch, 8*inch, letter[1] - 7.5*inch)
    
    #diagnosis heading
    text = "DIAGNOSIS AND ICD-10 CODES"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(white)
    c.drawCentredString(4.3*inch, letter[1] - 7.6*inch, text)
    red_text_style = ParagraphStyle(
    "RedText",
    parent=styles["Normal"],
    textColor=colors.red  # Set the text color to red
    )
    icd_desc_list = json.loads(report_data['icd_desc'])
    icd_codes_list = json.loads(report_data['icd_codes'])
    last_digit = report_data['diabetes_type'][-1]
    filtered_icd_codes = [code for code in icd_codes_list if code.endswith(last_digit)]
    print(filtered_icd_codes, "CHECK",icd_codes_list)
    if len(icd_codes_list) == 2:
        last_digit = report_data['diabetes_type'][-1]
        # filtered_icd_codes = [code for code in icd_codes_list if code[-2] == last_digit]
    elif len(icd_codes_list) == 1:
        filtered_icd_codes = [code for code in icd_codes_list]
    #Daignosis table
    table_data = [ 
        ("Condition", "Condition 2"),
        (f"Diagnosis {filtered_icd_codes}", [Paragraph(desc, styles["Normal"]) for desc in icd_desc_list]),
        ("Screening Result", Paragraph(report_data['summary'],
               red_text_style))
    ]
    colWidths = [1.9*inch, 5.6*inch, 5.6*inch] 

    table_style = [
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#208295")),
        ("TEXTCOLOR", (0, 0), (0, -1), white),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), 
        ("BOTTOMPADDING", (0, 0), (0, -1), 10),                         #bottom pading
        ("BACKGROUND", (1, 0), (-1, -1), HexColor("#ECECEC")),
        ("GRID", (0, 0), (-1, -1), 1, black), 
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ]

    # Create the table
    table = Table(table_data, colWidths=colWidths, rowHeights=[0.4*inch, 0.7*inch, 0.5*inch])
    table.setStyle(TableStyle(table_style))

    # Draw the table on the canvas
    table_x = 0.5*inch
    table_y = letter[1] - 9.3*inch
    table.wrapOn(c, 0, 0)
    table.drawOn(c, table_x, table_y)

    #Recomendation heading
    c.setStrokeColor(HexColor("#208295"))  # Use a blue color for the line
    c.setLineWidth(17) 
    c.line(0.5*inch, letter[1] - 9.72*inch, 8*inch, letter[1] - 9.72*inch)

    text = "RECOMMENDATION"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(white)
    c.drawCentredString(4.3*inch, letter[1] - 9.82*inch, text)

    #BOX FOR RECOMMENDATION
    box_rwidth = 7.5*inch
    box_rheight = 1*inch
    box_rx = 0.5*inch
    box_ry = letter[1] - 10.6*inch
    box_rborder_width = 1

    c.setStrokeColor(HexColor("#000000"))  # Black color for the border
    c.setLineWidth(box_rborder_width)
    c.rect(box_rx, box_ry, box_rwidth, box_rheight, fill=False, stroke=True)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    field_rx_left = box_rx + 10
    field_ry = box_ry + 10
    current_year = current_datetime.year
    is_leap_year = (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0)

# Calculate the number of days in the year (adjust for leap years)
    days_in_a_year = 366 if is_leap_year else 365

# Calculate the follow-up date (next year, one day before current)
    followup_datetime = current_datetime + timedelta(days=days_in_a_year + 1)
    formatted_followup_date = followup_datetime.strftime('%d-%b-%Y')
    point_1 = f"1. Consult an Ophthalmologist within 12 months, preferably before {formatted_followup_date}"
    
    before_date = current_datetime + timedelta(days=days_in_a_year - 8)
    formatted_before_date = before_date.strftime('%d-%b-%Y')
    after_date = current_datetime + timedelta(days=days_in_a_year + 8)
    formatted_after_date = after_date.strftime('%d-%b-%Y')
    point_2 = f"2. Get your eyes screened for DR on {report_data['username']} at Clinic between {formatted_before_date} & {formatted_after_date}"
    c.drawString(field_rx_left, field_ry + 20, f"{point_1}")
    c.drawString(field_rx_left, field_ry + 5, f"{point_2}")
    c.showPage()
    #***************************** page 1 ends ****************************

    #Disclamer
    c.setStrokeColor(HexColor("#208295"))  # Use a blue color for the line
    c.setLineWidth(17) 
    c.line(0.5*inch, letter[1] - 0.5*inch, 8*inch, letter[1] - 0.5*inch)

    text = "DISCLAIMER"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(white)
    c.drawCentredString(4.3*inch, letter[1] - 0.6*inch, text)

    #PARAGRAPH

    content = ("This report is generated by an Artificial Intelligence software, an initiative of BioScan AI Innovative\n"
            "Solutions, and is for informational purposes only. This report is indicative and assistive in nature and is\n"
            "not a replacement for medical advice, diagnosis or treatment. Accrodingly, before taking any action upon such information, we encourage you to consult with the appropriate professionals, We do not provide any medical/ health advice.")
    # Create a Paragraph object with the 'Normal' style
    modified_style = styles['Normal']

    modified_style.fontSize = 8
    modified_style.leading = 10
    paragraph = Paragraph(content, style=modified_style)

    # Convert inch measurements to points
    x_pos = 0.5 * inch  # X position in inches (1.5 inches)
    y_pos = 2.44 * inch  # Y position in inches (10 inches)
    width = 7 * inch   # Width in inches (5 inches)
    height = 1 * inch  # Height in inches (4 inches)

    # Draw the paragraph on the canvas
    paragraph.wrapOn(c, width, height)
    paragraph.drawOn(c, x_pos, letter[1] - y_pos)

    #DISCLAIMER IMAGE
    # image1_path = "D:/maskottchen/zia-project/pdf_report/disclaimer.png"
    # image1_path = "dristieye/static/images/doctor.png"
    # image1 = ImageReader(image1_path)

    # Calculate image positions and dimensions
    image_width = 6.5*inch
    image_height = 4.0*inch
    image1_x = 0.8*inch
    image_y = letter[1] - 6.6*inch

    # Draw the images on the canvas
    # c.drawImage(image1, image1_x, image_y, width=image_width, height=image_height)
 
   # Save the canvas and finalize the PDF
    
    c.showPage()
    c.save()

    # subject = 'Verify your email address'
    # message = 'Your Report is Ready'
    # print(request.user.email,'EMAIL')
    # send_mail(subject, message, 'boredstuff2021@gmail.com', [request.user.email])
    # Send an email with the PDF attached

    # Create a PDF file
    # c = canvas.Canvas(pdf_file)
    
    subject = 'Your Report is Ready'
    message = 'Your Report is Ready'
    from_email = 'boredstuff2021@gmail.com'
    recipient_email = request.user.email 

    # Create an email message with the PDF as an attachment
    email = EmailMessage(subject, message, from_email, [recipient_email])
    email.attach('report.pdf', response.getvalue(), 'application/pdf')
    # Send the email
    email.send()
    return response
    
        



# Pending Request (doctor)
def pendingRequest(request):
    response = requests.get('http://127.0.0.1:8000/credit_requset_list/')
    doctor_id=[]
    doctor_names=[]
    req_date= []
    re_cre_val = []
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # data = json.loads(response.text)
        print(data)
        data = json.loads(data)
        # print(type(data), 'TYPE')
        for item in data:
            # Access the 'fields' dictionary within each object and then the 'doctor' field
            doctor = item['fields']['doctor']
            # Retrieve the doctor object from the database using the ID
            doctor = Doctor.objects.get(id=doctor)

            # Access the 'fullname' attribute of the doctor object
            # doctor_name = doctor.fullname

            # doctor_names.append(doctor_name)

            r_date = item['fields']['request_date']
            r_credit = item['fields']['credit_value']
            doctor_id.append(doctor)
            req_date.append(r_date)
            re_cre_val.append(r_credit)
            # print(doctor_id,re_cre_val, req_date)
        data = list(zip(doctor_id, req_date, re_cre_val))
    return render(request,'doctorpanel/pendingRequest.html', {'data': data,})

# Success Request (doctor)
def successRequest(request):
    return render(request,'doctorpanel/successRequest.html')

# Rejected Request (doctor)
def rejectedRequest(request):
    return render(request,'doctorpanel/rejectedRequest.html')

# Search Reports (doctor)
def searchReports(request):
    return render(request,'doctorpanel/searchReports.html')

# Chart (doctor)
def charts(request):
    patients_by_day = list(patients_by_weekday())
    print(patients_by_day)
    context={
        'patients_by_day':patients_by_day
    }
    return render(request,'doctorpanel/charts.html', context)

# Request Credit (doctor)
def requestCredit(request):
    if request.method == 'POST':
        
        form = CreditRequestForm(request.POST)
        if form.is_valid():
            # Get the currently logged-in doctor
            doctor = request.user
            
            # Extract credit_value from the form
            credit_value = form.cleaned_data['credit_value']
            
            # Create a CreditRequest associated with the logged-in doctor
            CreditRequest.objects.create(doctor=doctor, credit_value=credit_value)
            
            user = request.user

            if user.is_superuser:
                return redirect('admin_home')
            # Redirect to a success page or wherever you need to go
            return redirect('doctorDashboard')
                
    else:
        form = CreditRequestForm()

    return render(request, 'doctorpanel/requestCredit.html', {'form': form})
    # return render(request,'doctorpanel/requestCredit.html')

def error(request):
    return render(request,'error.html')

def mail_error(request):
    return render(request,'mail_error.html')

def general_error(request):
    return render(request,'general_error.html')