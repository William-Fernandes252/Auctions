from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import generics, views
from auctions.models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.classes import CsrfExemptSessionAuthentication
from rest_framework.exceptions import PermissionDenied
from .mixins import UserListingsQuerysetMixin, ListingQuerysetMixin


class HomeAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('listing-list'))
    
api_home_view = HomeAPIView.as_view()
    

class UserHomeAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
            return HttpResponseRedirect(reverse('user-listing-list'))
        
user_home_api_view = UserHomeAPIView.as_view()


class ListingListAPIView(ListingQuerysetMixin, generics.ListAPIView):
    serializer_class = ListingAbstractSerializer
    permission_classes = (AllowAny,)
    
listing_list_view = ListingListAPIView.as_view()


class ListingDetailsAPIView(ListingQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = ListingDetailsSerializer
    lookup_field = 'pk'
    pagination_class = None
    
listing_details_view = ListingDetailsAPIView.as_view()


class ListingCreateAPIView(generics.CreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingCreationSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
         
listing_create_view = ListingCreateAPIView.as_view()


class BidListAPIView(generics.ListAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidListSerializer
    permission_classes = (IsAuthenticated,)
    
bid_list_view = BidListAPIView.as_view()


class ListingBidListView(generics.ListCreateAPIView):
    serializer_class = BidAbstractSerializer
    lookup_field ='pk'
    pagination_class = None
    
    def get_queryset(self):
        return Listing.objects.get(pk=self.kwargs.get('pk')).bids
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied({"denied": "Must be authenticated to perform this action."})
        serializer.save(
            user=self.request.user, 
            listing=Listing.objects.get(pk=self.kwargs.get('pk'))
        )
        
listing_bid_list_view = ListingBidListView.as_view()


class ListingQuestionListAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    lookup_field = 'pk'
    pagination_class = None
    
    def get_queryset(self):
        return Listing.objects.get(pk=self.kwargs.get('pk')).questions
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied({"denied": "Must be authenticated to perform this action."})
        serializer.save(
            user=self.request.user, 
            listing=Listing.objects.get(pk=self.kwargs.get('pk'))
        )
    
listing_question_list_view = ListingQuestionListAPIView.as_view()


class WatchlistAPIView(generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return self.request.user.watchlist.all()
    
user_watchlist_api_view = WatchlistAPIView.as_view()


class UserListingsAPIView(UserListingsQuerysetMixin, generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = (IsAuthenticated,)
    
user_listing_list_view = UserListingsAPIView.as_view()


class UserBidsAPIView(generics.ListAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

user_bid_list_view = UserBidsAPIView.as_view()


class EditListingAPIView(UserListingsQuerysetMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ListingEditSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field ='pk'
    
    def update(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            raise PermissionDenied(
                {"denied": "Only the author of a listing is allowed to edit it."}
            )
        return super(EditListingAPIView, self).update(request, *args, **kwargs)
    
user_listing_details_view = EditListingAPIView.as_view()


class WatchListingAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        listing = generics.get_object_or_404(Listing, pk=data.get('id'))
        watchlist = request.user.watchlist
        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)
        return Response(status=200)
    
watch_listing = WatchListingAPIView.as_view()


class AnswerQuestionAPIView(generics.GenericAPIView):
    serializer_class = AnswerCreationSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, **kwargs):
        listing = generics.get_object_or_404(Listing, pk=kwargs.get('listing_pk'))
        question = generics.get_object_or_404(Question, pk=kwargs.get('question_pk'), listing=listing)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if listing.author != request.user:
            raise PermissionDenied({"denied": "Only the author of the listing is allowed to answer questions."})
        
        question.answer = serializer.save(author=request.user)
        question.save()
        
        return Response(serializer.data, status=201)
    
answer_question_view = AnswerQuestionAPIView.as_view()