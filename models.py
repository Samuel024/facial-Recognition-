from django.db import models
import tensorflow as tf
import os
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

class UserProfile(models.Model):
    image = models.ImageField(upload_to='profile_images/')
