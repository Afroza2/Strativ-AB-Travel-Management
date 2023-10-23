from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=20, default='meow')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Encrypt the password before saving to the database
        self.set_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username