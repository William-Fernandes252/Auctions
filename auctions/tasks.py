from celery import shared_task


@shared_task(bind=True)
def compute_winner(listing) -> None:
    listing.winner = listing.bids.first().user