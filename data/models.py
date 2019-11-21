import sys

try:
    from django.db import models
except  Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

# Sample User model
class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    class Meta:
        db_table = "users_customuser"

# class Company(models.Model):
#     name = models.CharField(max_length=100)

#     class Meta:
#         db_table = "account_company"

#CHAT
# from django.utils import timezone
class Connection(models.Model):
    connection_id = models.CharField(max_length=255)

class Room(models.Model):
    name = models.CharField(max_length=100)

class Message(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    user_profile_img = models.TextField(
        default='https://res.cloudinary.com/louiseyoma/image/upload/v1546701687/profile_pic.png'
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    timestamp=models.CharField(max_length=100,null=True)
    # timestamp = models.DateTimeField(default=timezone.now, null=False)
