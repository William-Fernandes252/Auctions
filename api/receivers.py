from datetime import datetime


def get_timestamp():
    return datetime.now().strftime("%d/%B/%Y %H:%M:%S")


def notify_listing_closed(sender, **kwargs):
    listing = kwargs.get('instance')
    if listing.ended_manually:
        print(f'[{get_timestamp()}] "The listing {listing} has been closed."')
        
        
def notify_listing_created(sender, **kwargs):
    listing = kwargs.get('instance')
    if not kwargs.get('created'):
        return
    print(f'[{get_timestamp()}] "The listing {listing} has been created."')
    
    
def notify_bid(sender, **kwargs):
    bid = kwargs.get('instance')
    print(f'[{get_timestamp()}] "{bid.user} offered {bid.value} on {bid.listing}."')
    
    
def notify_question_pub(sender, **kwargs):
    question = kwargs.get('instance')
    print(f'[{get_timestamp()}] "{question.user} published a question on {question.listing}."')
    
    
def notify_answer_pub(sender, **kwargs):
    answer = kwargs.get('instance')
    print(f'[{get_timestamp()}] "{answer.author} answered a question."')