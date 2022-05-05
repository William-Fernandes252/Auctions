from django.http import HttpResponseRedirect
from django import urls
from rest_framework.response import Response
from rest_framework import generics, views
from auctions import models
from . import serializers, permissions as api_permissions
from rest_framework import permissions, exceptions
from authentication import classes
from . import mixins as api_mixins
    

class UserHomeAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
            return HttpResponseRedirect(urls.reverse('user-listing-list'))
        
user_home_api_view = UserHomeAPIView.as_view()


class ListingListAPIView(api_mixins.ListingQuerysetMixin, generics.ListAPIView):
    serializer_class = serializers.ListingAbstractSerializer
    
listing_list_view = ListingListAPIView.as_view()


class ListingDetailsAPIView(api_mixins.ListingQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = serializers.ListingDetailsSerializer
    lookup_field = 'pk'
    pagination_class = None
    
listing_details_view = ListingDetailsAPIView.as_view()


class ListingCreateAPIView(generics.CreateAPIView):
    queryset = models.Listing.objects.all()
    serializer_class = serializers.ListingCreationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
         
listing_create_view = ListingCreateAPIView.as_view()


class BidListAPIView(generics.ListAPIView):
    queryset = models.Bid.objects.all()
    serializer_class = serializers.BidListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
bid_list_view = BidListAPIView.as_view()


class ListingBidListView(generics.ListCreateAPIView):
    serializer_class = serializers.BidAbstractSerializer
    lookup_field ='pk'
    pagination_class = None
    
    def get_queryset(self):
        return models.Listing.objects.get(pk=self.kwargs.get('pk')).bids
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied({"denied": "Must be authenticated to perform this action."})
        serializer.save(
            user=self.request.user, 
            listing=models.Listing.objects.get(pk=self.kwargs.get('pk'))
        )
        
listing_bid_list_view = ListingBidListView.as_view()


class ListingQuestionListAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.QuestionSerializer
    lookup_field = 'pk'
    pagination_class = None
    
    def get_queryset(self):
        return models.Listing.objects.get(pk=self.kwargs.get('pk')).questions
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied({"denied": "Must be authenticated to perform this action."})
        serializer.save(
            user=self.request.user, 
            listing=models.Listing.objects.get(pk=self.kwargs.get('pk'))
        )
    
listing_question_list_view = ListingQuestionListAPIView.as_view()


class WatchlistAPIView(generics.ListAPIView):
    serializer_class = serializers.ListingListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return self.request.user.watchlist.all()
    
user_watchlist_api_view = WatchlistAPIView.as_view()


class UserListingsAPIView(api_mixins.UserListingsQuerysetMixin, generics.ListAPIView):
    serializer_class = serializers.ListingListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
user_listing_list_view = UserListingsAPIView.as_view()


class UserBidsAPIView(generics.ListAPIView):
    queryset = models.Bid.objects.all()
    serializer_class = serializers.BidListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

user_bid_list_view = UserBidsAPIView.as_view()


class EditListingAPIView(api_mixins.UserListingsQuerysetMixin, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ListingEditSerializer
    permission_classes = (permissions.IsAuthenticated, api_permissions.IsOwner)
    lookup_field ='pk'
    
user_listing_details_view = EditListingAPIView.as_view()


class WatchListingAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        listing = generics.get_object_or_404(models.Listing, pk=data.get('id'))
        watchlist = request.user.watchlist
        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)
        return Response(status=200)
    
watch_listing = WatchListingAPIView.as_view()


class AnswerQuestionAPIView(generics.GenericAPIView):
    serializer_class = serializers.AnswerCreationSerializer
    authentication_classes = (classes.CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, api_permissions.IsOwner)
    
    def post(self, request, **kwargs):
        listing = generics.get_object_or_404(
            models.Listing, 
            pk=kwargs.get('listing_pk')
        )
        question = generics.get_object_or_404(
            models.Question, 
            pk=kwargs.get('question_pk'), 
            listing=listing
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if listing.author != request.user:
            raise exceptions.PermissionDenied(
                {"denied": "Only the author of the listing is allowed to answer questions."}
            )
        
        question.answer = serializer.save(author=request.user)
        question.save()
        
        return Response(serializer.data, status=201)
    
answer_question_view = AnswerQuestionAPIView.as_view()