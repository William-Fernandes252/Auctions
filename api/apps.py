from django.apps import AppConfig
from . import receivers
from django.db.models import signals


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        from auctions.models import Listing, Bid, Question, Answer
        
        signals.post_save.connect(
            receivers.notify_listing_closed,
            sender=Listing,
            dispatch_uid='listing_closed'
        )
        signals.post_save.connect(
            receivers.notify_listing_created,
            sender=Listing,
            dispatch_uid='listing_created'
        )
        signals.post_save.connect(
            receivers.notify_bid,
            sender=Bid,
            dispatch_uid='bid_posted'
        )
        signals.post_save.connect(
            receivers.notify_question_pub,
            sender=Question,
            dispatch_uid='question_pub'
        )
        signals.post_save.connect(
            receivers.notify_answer_pub,
            sender=Answer,
            dispatch_uid='answer_pub'
        )