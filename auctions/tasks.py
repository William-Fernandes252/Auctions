from celery import shared_task


@shared_task(bind=True, name="set_winner")
def set_listing_winner_task(listing_id: int):
    from .models import Listing
    from django.shortcuts import get_object_or_404
    
    listing = get_object_or_404(Listing, id=listing_id)
    
    if not listing.bids.all().exists() or listing.winner.exists():
        return
    
    listing.winner = listing.bids.first().user
    listing.save()