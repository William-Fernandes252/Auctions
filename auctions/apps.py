from django.apps import AppConfig
from . import receivers
from django.db.models import signals
import sys


class AuctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auctions'
    
    
    def ready(self):
        if 'test' in sys.argv:
            return # Disable signals during tests
        
        Listing = self.get_model('Listing')
        signals.post_save.connect(
            receivers.set_winner,
            sender=Listing,
            dispatch_uid='set-winner'
        )