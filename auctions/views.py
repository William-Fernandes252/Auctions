from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django import http, shortcuts, urls
from django.core.paginator import Paginator
from django.utils import timezone
from . import forms, models
from django.views.generic import base as base_views
from django.views import generic


BASE_TITLE = "Auctions |"


class IndexView(base_views.TemplateView):
    template_name = 'auctions/index.html'
    see_watchlist = False
    see_search_results = False
    
    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        
        if kwargs.get('category'):
            context['category'] = kwargs.get('category')
            listings = models.Listing.objects.active().filter(
                category__name=context['category'],
            )
            context['title'] = context['category']
            
        elif self.see_watchlist:
            listings = self.request.user.watchlist.active()
            context['title'] = 'Watchlist'
            
        elif self.see_search_results:
            q = self.request.GET["q"]
            listings = models.Listing.objects.active().search(q)
            context['title'] = f'Search Results for "{q}"'
            
        else:
            listings = models.Listing.objects.active()
            context['title'] = 'Active Listings'
            
        paginator = Paginator(listings, 50)
        page_number = self.request.GET.get('page')
        context['categories'] = models.Category.objects.all()
        context['listings'] = paginator.get_page(page_number)
        context['latest_bids'] = models.Bid.objects.all()[:5]
        
        return context
    
    
class ListingListView(generic.ListView):
    template_name = 'auctions/index.html'
    queryset = models.Listing.objects.active()
    ordering = ('end_time',)
    paginate_by = 10
    watchlist = False

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        if category := kwargs.get('category'):
            queryset = queryset.from_category(category)
        elif self.watchlist:
            queryset = self.request.user.watchlist.active()
        elif q := self.request.GET.get('q'):
            queryset = queryset.search(query=q)
        return queryset
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = "Active Listings"
        if category := kwargs.get('category'):
            context['title'] = f"{category.title()}"
        elif self.watchlist:
            context['title'] = f"Watchlist"
        elif q := self.request.GET.get('q'):
            context['title'] = f"Search results for {q}"  
        context['latest_bids'] = models.Bid.objects.all()[:5]
        return context
        
        
@auth_decorators.login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        form = forms.ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.author = request.user
            listing.save()
            messages.success(request, "Auction started!")
            return http.HttpResponseRedirect(urls.reverse("listing", kwargs={'listing_id': listing.id}))
        else:
            return shortcuts.render(request, "auctions/create.html", {
                "form": form
            })
    return shortcuts.render(request, "auctions/create.html", {
        "form": forms.ListingForm()
    })


def listing_view(request, listing_id):
    listing = shortcuts.get_object_or_404(models.Listing, id=listing_id)

    context = {}
    context['listing'] = listing
    context['finished'] = listing.is_finished()
    if context['finished']:
        return shortcuts.render(request, "auctions/listing.html", context)
        
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
        context['highest_bid'] = models.listing.bids.first().value
        context['current_bid'] = request.user.bids.filter(listing=listing).first() == listing.bids.first()
    except AttributeError:
        context['highest_bid'] = False
        
    context['author'] = request.user == listing.author
    context["bid_form"] = forms.BidForm()
    context["question_form"] = forms.QuestionForm()
    
    return shortcuts.render(request, "auctions/listing.html", context)
    
    
@auth_decorators.login_required(login_url='login')
def bid(request, listing_id):
    bid_form = forms.BidForm(request.POST)
    
    if bid_form.is_valid():
        listing = models.Listing.objects.get(pk=listing_id)
        new_bid = bid_form.save(commit=False)
        current_bids = models.Bid.objects.filter(listing=listing)
        is_highest = all(new_bid.value > n.value for n in current_bids)
        is_valid = new_bid.value > models.listing.initial_price
        if not is_valid:
            messages.error(request, "Bid denied. A bid must exceed the intial price.")
        elif is_valid and is_highest:
            new_bid.listing = listing
            new_bid.user = request.user
            new_bid.save()
            messages.success(request, "Bid posted!")
        
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'listing_id': listing.id}))


@auth_decorators.login_required(login_url='login')
def close_listing(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    if request.user == models.listing.user:
        listing.ended_manually = True
        listing.save()
        messages.success(request, "Auction closed! Wait until the winner to get in touch.")
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'listing_id': listing.id}))
    

@auth_decorators.login_required(login_url='login')
def add_question(request, listing_id):
    question_form = models.Question(request.POST)
    if question_form.is_valid():
        new_question = question_form.save(commit=False)
        new_question.listing = models.Listing.objects.get(pk=listing_id)
        new_question.user = request.user
        new_question.save()
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'listing_id': listing_id}))


@auth_decorators.login_required(login_url='login')
def watch(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    watchings = request.user.watchlist
    if listing in watchings.all():
        watchings.remove(listing)
    else:
        watchings.add(listing)
    return http.HttpResponseRedirect(urls.reverse("listing", kwargs={'listing_id': listing_id}))


@auth_decorators.login_required(login_url='login')
def watchlist(request):
    return shortcuts.render(request, "auctions/index.html", {
        "listings": request.user.watchlist.all(),
        "title": "Watchlist"
    })