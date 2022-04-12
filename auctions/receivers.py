from . import tasks


def set_winner(sender, **kwargs):
    listing = kwargs.get('instance')
    
    if not listing.bids.all().exists():
        return
    
    if listing.ended_manually:
        listing.winner = listing.bids.first().user
        return
    
    elif kwargs.get('created'):
        tasks.compute_winner.apply_async(listing, eta=listing.end_time)