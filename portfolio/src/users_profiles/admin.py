from django.contrib import admin

# Register your models here.
from users_profiles.models import UserProfile

admin.site.register(UserProfile)
