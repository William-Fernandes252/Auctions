from django.apps import AppConfig
from django.db.models import signals
from . import receivers
from sys import argv


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        if 'test' in argv:
            return # Disable signals during tests
        
        User = self.get_model('User')
        signals.post_save.connect(
            receivers.new_user, 
            sender=User, 
            dispatch_uid='new_user'
        )