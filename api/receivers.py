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
    print(f'[{get_timestamp()}] "The listing {listing.name} has been created."')
    
    
def notify_bid(sender, **kwargs):
    bid = kwargs.get('bid')
    print(f'[{get_timestamp()}] "{bid.user} offered {bid.value} on {bid.listint}."')
    
    
def notify_question_pub(sender, **kwargs):
    question = kwargs.get('question')
    print(f'[{get_timestamp()}] "{question.user} published a question on {question.listint}."')
    
    
def notify_answer_pub(sender, **kwargs):
    answer = kwargs.get('answer')
    print(f'[{get_timestamp()}] "{answer.author} answered {answer.question.user} on {answer.question.listint}."')