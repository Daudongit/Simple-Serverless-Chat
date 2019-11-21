# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from data.models import *


#Add user
# user = User(name="masnun", email="masnun@gmail.com")
# user.save()

# Application logic
# first_user = User.objects.all()[0]

# print(first_user.username)
# print(first_user.email)
# Room.objects.filter(id=1).delete()
# Room(id=2, name='room2').save()
# Message(
#     username='username',
#     content='content',
#     timestamp='current time',
#     user_profile_img='imag.jpg',
#     room=root,
# ).save()
import time
Message(
    username='username'+str(time.time()),
    content='content',
    timestamp='current time',
    # user_profile_img='imag.jpg',
    room_id=2,
).save()

print('successfuly saved')