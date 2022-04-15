from celery import shared_task
from celery.utils import log


logger = log.get_task_logger(__name__)

@shared_task(name="set_winner")
def set_listing_winner_task(pk):
    from .models import Listing
    from django.shortcuts import get_object_or_404
    
    listing = get_object_or_404(Listing, pk=pk)
    
    if not listing.bids.all().exists() or listing.winner.exists():
        return
    
    listing.winner = listing.bids.first().user
    listing.save()
    
    logger.info(f"Auction {listing} completion has been scheduled.")