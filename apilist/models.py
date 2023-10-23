from django.db import models

# Create your models here.
from django.contrib.auth.hashers import make_password

class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=20, default='meow')

    def save(self, *args, **kwargs):
        # Encrypt the password before saving to the database
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username