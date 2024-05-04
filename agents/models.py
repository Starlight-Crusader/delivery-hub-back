from django.db import models
# from django.contrib.auth.hashers import make_password


class Agent(models.Model):
    name = models.CharField(max_length=30, unique=True)

    CONSUMER = 1
    PROVIDER = 2

    TYPE_CHOISES = [
        (CONSUMER, 'Consumer'),
        (PROVIDER, 'Provider'),
    ]

    type = models.IntegerField(choices=TYPE_CHOISES)
    
    viewer_pass = models.CharField(max_length=128)
    worker_pass = models.CharField(max_length=128)
    manager_pass = models.CharField(max_length=128)

    REQUIRED_FIELDS = ['type', 'viewer_pass', 'worker_pass', 'manager_pass']
    USERNAME_FIELD = 'name'

    is_anonymous = False
    is_authenticated = True
