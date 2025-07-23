from django.contrib import admin
from .models import UserProfile


# Register your models here.


class Usercustom(admin.ModelAdmin):
    list_display = ('id', 'image') 


admin.site.register(UserProfile, Usercustom)

