from django.contrib import admin
from .models import CustomUser, AdminProfile, StaffProfile

admin.site.register(CustomUser)
admin.site.register(AdminProfile)
admin.site.register(StaffProfile)
