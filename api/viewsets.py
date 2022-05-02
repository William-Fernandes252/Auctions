from rest_framework import viewsets, mixins, decorators, status, generics
from rest_framework.response import Response
from . import serializers
from rest_framework import permissions
from . import mixins as api_mixins
from auctions import models


class ListingViewSet(viewsets.GenericViewSet,
                     api_mixins.ListingQuerysetMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin):
    
    queryset = models.Listing.objects.active()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    serializer_classes = {
        'list': serializers.ListingAbstractSerializer,
        'retrieve': serializers.ListingDetailsSerializer,
        'create': serializers.ListingCreationSerializer,
        'bids_list': serializers.BidAbstractSerializer,
        'bids_create': serializers.BidAbstractSerializer,
        'questions_list': serializers.QuestionSerializer,
        'questions_create': serializers.QuestionSerializer,
    }
    
    
    def get_queryset(self):
        if 'bids' in self.action:
            return models.Listing.objects.get(pk=self.kwargs.get('pk')).bids
        elif 'questions' in self.action:
            return models.Listing.objects.get(pk=self.kwargs.get('pk')).questions
        
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if q is not None:
            queryset = queryset.search(query=q)
        if category is not None:
            queryset = queryset.from_category(category)
        return queryset
    
    
    def get_serializer_class(self):
        """Instantiates and returns the serializer for the given action.
        """
        return self.serializer_classes.get(self.action)

    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
                
            
    @decorators.action(
        detail=True,  
        methods=['get'],
        name='Listing Bids List', 
        pagination_class = None,
    )
    def bids_list(self, request, pk=None):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @decorators.action(
        detail=True,
        methods=['post'],
        name='Post Bid',
        permission_classes=[permissions.IsAuthenticated],
    )
    def bids_create(self, request, pk=None):        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user, 
            listing=models.Listing.objects.get(pk=pk)
        )
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    
    
    @decorators.action(
        detail=True,
        methods=['get'],
        name='Listing Questions List',
        pagination_class = None,
    )
    def questions_list(self, request, pk=None):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @decorators.action(
        detail=True,
        methods=['post'],
        name='Publish Question',
        permission_classes=[permissions.IsAuthenticated],
    )
    def questions_create(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user, 
            listing=models.Listing.objects.get(pk=pk)
        )
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    
    
    @decorators.action(
        detail=False,
        methods=['post'],
        name='Watch Listing',
    )
    def watch(request):
        listing = generics.get_object_or_404(models.Listing, pk=request.data.get('id'))
        watchlist = request.user.watchlist
        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)
        return Response(status=status.HTTP_200_OK)
    
    
      
listing_list_view = ListingViewSet.as_view({'get': 'list'})
listing_detail_view = ListingViewSet.as_view({'get': 'retrieve'})
listing_create_view = ListingViewSet.as_view({'post': 'create'})
listing_bid_list_view = ListingViewSet.as_view({'get': 'bids_list'})
listing_bid_create_view = ListingViewSet.as_view({'post': 'bids_create'})
listing_question_list_view = ListingViewSet.as_view({'get': 'questions_list'})
listing_question_create_view = ListingViewSet.as_view({'post': 'questions_create'})