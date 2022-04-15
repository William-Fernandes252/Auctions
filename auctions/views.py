from django.contrib import messages
from django.contrib.auth import (
    decorators as auth_decorators, 
    mixins as auth_mixins)
from django import http, urls
from django.utils import timezone
from . import forms, models
from django.views import generic
    
    
class ListingListView(generic.ListView):
    template_name = 'auctions/index.html'
    queryset = models.Listing.objects.active()
    ordering = ('end_time',)
    paginate_by = 10
    watchlist = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if category := self.kwargs.get('category'):
            queryset = queryset.from_category(category=category)
        elif self.watchlist:
            queryset = self.request.user.watchlist.active()
        elif q := self.request.GET.get('q'):
            queryset = queryset.search(query=q)
        return queryset
            
    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = "Active Listings"
        if category := self.kwargs.get('category'):
            context['title'] = f"{category.title()}"
        elif self.watchlist:
            context['title'] = f"Watchlist"
        elif q := self.request.GET.get('q'):
            context['title'] = f"Search results for {q}"  
        context['latest_bids'] = models.Bid.objects.all()[:5]
        return context
            
    
class ListingCreateView(auth_mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Listing
    template_name = "auctions/create.html"
    form_class = forms.ListingForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Auction started!")
        return super().form_valid(form)
    
    
class ListingDetailsView(generic.DetailView):
    model = models.Listing
    template_name = "auctions/listing.html"
    context_object_name = "listing"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = context['listing']
        context['finished'] = listing.is_finished()
        if context['finished']:
            return context
            
        time_remaining = listing.end_time - timezone.now()
        context['days'] = time_remaining.days
        context['hours'] = int(time_remaining.seconds/3600)
        context['minutes'] = int(
            time_remaining.seconds/60 - (context['hours'] * 60)
        )
        
        context['is_author'] = self.request.user == listing.author
        
        context['watching'] = False
        if self.request.user.watchlist.all().exists():
            context['watching'] = listing in self.request.user.watchlist.all()

        context['highest_bid'] = False
        if listing.bids.exists():
            context['highest_bid'] = listing.bids.all().first()
        
        context['is_usr_curr_bid'] = False
        if self.request.user.bids.filter(listing=listing).exists():
            usr_curr_bid = self.request.user.bids.filter(listing=listing).first()
            context['is_usr_curr_bid'] = usr_curr_bid == listing.bids.first()
            
        context["bid_form"] = forms.BidForm()
        context["question_form"] = forms.QuestionForm()
        
        return context
    
   
@auth_decorators.login_required
def bid(request, pk):
    bid_form = forms.BidForm(request.POST)
    
    if bid_form.is_valid():
        listing = models.Listing.objects.get(pk=pk)
        new_bid = bid_form.save(commit=False)
        current_bids = models.Bid.objects.filter(listing=listing)
        is_highest = all(new_bid.value > n.value for n in current_bids)
        is_valid = new_bid.value > listing.initial_price
        if not is_valid:
            messages.error(request, "Bid denied. A bid must exceed the intial price.")
        elif is_valid and is_highest:
            new_bid.listing = listing
            new_bid.user = request.user
            new_bid.save()
            messages.success(request, "Bid posted!")
        
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'pk': listing.id}))


@auth_decorators.login_required
def close_listing(request, pk):
    listing = models.Listing.objects.get(pk=pk)
    if request.user == models.listing.user:
        listing.ended_manually = True
        listing.save(update_fields=['ended_manually'])
        messages.success(request, "Auction closed! Wait until the winner to get in touch.")
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'pk': listing.id}))
    

@auth_decorators.login_required
def add_question(request, pk):
    question_form = models.Question(request.POST)
    if question_form.is_valid():
        new_question = question_form.save(commit=False)
        new_question.listing = models.Listing.objects.get(pk=pk)
        new_question.user = request.user
        new_question.save()
    return http.HttpResponseRedirect(urls.reverse('listing', kwargs={'pk': pk}))


@auth_decorators.login_required
def watch(request, pk):
    listing = models.Listing.objects.get(pk=pk)
    watchings = request.user.watchlist
    if listing in watchings.all():
        watchings.remove(listing)
    else:
        watchings.add(listing)
    return http.HttpResponseRedirect(urls.reverse("listing", kwargs={'pk': pk}))