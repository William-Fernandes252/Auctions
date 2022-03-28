from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from auctions.models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.classes import CsrfExemptSessionAuthentication
from rest_framework.exceptions import PermissionDenied


@api_view(["GET"])
def api_home(request, *args, **kwargs):
    return Response({"message": "Hello there :D"})


class ListingListAPIView(generics.ListAPIView):
    queryset = Listing.objects.active()
    serializer_class = ListingListSerializer
    permission_classes = (AllowAny,)
    
listing_list_view = ListingListAPIView.as_view()


class ListingDetailsAPIView(generics.RetrieveAPIView):
    queryset = Listing.objects.active()
    serializer_class = ListingDetailsSerializer
    lookup_field = 'pk'
    pagination_class = None
    
listing_details_view = ListingDetailsAPIView.as_view()


class ListingCreateAPIView(generics.CreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingCreationSerializer
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Must be authenticated to perform this action.")
        serializer.save(author=self.request.user)
         
listing_create_view = ListingCreateAPIView.as_view()


class BidListAPIView(generics.ListAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidListSerializer
    
bid_list_view = BidListAPIView.as_view()


class ListingBidListView(generics.ListCreateAPIView):
    serializer_class = BidAbstractSerializer
    lookup_field ='pk'
    pagination_class = None
    
    def get_queryset(self):
        return Listing.objects.get(pk=self.kwargs.get('pk')).bids
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Must be authenticated to perform this action.")
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
            raise PermissionDenied("Must be authenticated to perform this action.")
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
    
watchlist_api_view = WatchlistAPIView.as_view()


class UserListingsAPIView(generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return self.request.user.listings.all()
    
user_listings_view = UserListingsAPIView.as_view()


class WatchListingAPIView(generics.GenericAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        listing = get_object_or_404(Listing, pk=data.get('id'))
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
    
    def post(self, request, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=kwargs.get('listing_pk'))
        question = get_object_or_404(Question, pk=kwargs.get('question_pk'), listing=listing)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if listing.author != request.user:
            raise PermissionDenied({"Denied": "Only the author of the listing is allowed to answer questions."})
        
        question.answer = serializer.save(author=request.user, question=question)
        question.save()
        
        return Response(serializer.data, status=201)
    
answer_question_view = AnswerQuestionAPIView.as_view() 