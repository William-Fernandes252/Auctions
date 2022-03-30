from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import BidForm, QuestionForm, ListingForm
from .models import Listing, Bid, Question, Category
from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = 'auctions/index.html'
    see_watchlist = False
    see_search_results = False
    
    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        
        if kwargs.get('category'):
            context['category'] = kwargs.get('category')
            listings = Listing.objects.active().filter(
                category__name=context['category'],
            )
            context['title'] = context['category']
            
        elif self.see_watchlist:
            listings = self.request.user.watchlist.active()
            context['title'] = 'Watchlist'
            
        elif self.see_search_results:
            q = self.request.GET["q"]
            listings = Listing.objects.active().search(q)
            context['title'] = f'Search Results for "{q}"'
            
        else:
            listings = Listing.objects.active()
            context['title'] = 'Active Listings'
            
        paginator = Paginator(listings, 50)
        page_number = self.request.GET.get('page')
        context['categories'] = Category.objects.all()
        context['listings'] = paginator.get_page(page_number)
        context['latest_bids'] = Bid.objects.all()[:5]
        
        return context
    
    
@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.author = request.user
            listing.save()
            messages.success(request, "Auction started!")
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing.id}))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })


def listing_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    context = {}
    context['listing'] = listing
    context['finished'] = listing.is_finished()
    if context['finished']:
        return render(request, "auctions/listing.html", context)
        
    time_remaining = listing.end_time - timezone.now()
    context['days'] = time_remaining.days
    context['hours'] = int(time_remaining.seconds/3600)
    context['minutes'] = int(time_remaining.seconds/60 - (context['hours'] * 60))
    
    try:
        context['watching'] = listing in request.user.watchlist.all()
    except AttributeError:
        context['watching'] = False
    context['author'] = request.user == listing.author
    
    try:
        context['highest_bid'] = listing.bids.first().value
        context['current_bid'] = request.user.bids.filter(listing=listing).first() == listing.bids.first()
    except AttributeError:
        context['highest_bid'] = False
        
    context['author'] = request.user == listing.author
    context["bid_form"] = BidForm()
    context["question_form"] = QuestionForm()
    
    return render(request, "auctions/listing.html", context)
    
    
@login_required(login_url='login')
def bid(request, listing_id):
    bid_form = BidForm(request.POST)
    
    if bid_form.is_valid():
        listing = Listing.objects.get(pk=listing_id)
        new_bid = bid_form.save(commit=False)
        current_bids = Bid.objects.filter(listing=listing)
        is_highest = all(new_bid.value > n.value for n in current_bids)
        is_valid = new_bid.value > listing.initial_price
        if not is_valid:
            messages.error(request, "Bid denied. A bid must exceed the intial price.")
        elif is_valid and is_highest:
            new_bid.listing = listing
            new_bid.user = request.user
            new_bid.save()
            messages.success(request, "Bid posted!")
        
    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))


@login_required(login_url='login')
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.user:
        listing.ended_manually = True
        listing.save()
        messages.success(request, "Auction closed! Wait until the winner to get in touch.")
    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))
    

@login_required(login_url='login')
def add_question(request, listing_id):
    question_form = Question(request.POST)
    if question_form.is_valid():
        new_question = question_form.save(commit=False)
        new_question.listing = Listing.objects.get(pk=listing_id)
        new_question.user = request.user
        new_question.save()
    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))


@login_required(login_url='login')
def watch(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchings = request.user.watchlist
    if listing in watchings.all():
        watchings.remove(listing)
    else:
        watchings.add(listing)
    return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))


@login_required(login_url='login')
def watchlist(request):
    return render(request, "auctions/index.html", {
        "listings": request.user.watchlist.all(),
        "title": "Watchlist"
    })