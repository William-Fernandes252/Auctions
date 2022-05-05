from rest_framework import viewsets, mixins, decorators, status, generics
from rest_framework.response import Response
from . import serializers
from rest_framework import permissions
from . import mixins as api_mixins
from auctions import models


class ListingViewSet(api_mixins.MultipleSerializersMixin,
                     viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin):

    queryset = models.Listing.objects.active()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_classes = {
        'list': serializers.ListingAbstractSerializer,
        'retrieve': serializers.ListingDetailsSerializer,
        'create': serializers.ListingCreationSerializer,
        'bids': serializers.BidAbstractSerializer,
        'create_bid': serializers.BidAbstractSerializer,
        'questions': serializers.QuestionSerializer,
        'pub_question': serializers.QuestionSerializer,
    }

    def get_queryset(self):
        if 'bid' in self.action:
            return models.Listing.objects.get(pk=self.kwargs.get('pk')).bids
        elif 'question' in self.action:
            return models.Listing.objects.get(pk=self.kwargs.get('pk')).questions

        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if q is not None:
            queryset = queryset.search(query=q)
        if category is not None:
            queryset = queryset.from_category(category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(
        detail=True,
        methods=['get'],
        pagination_class=None,
        name='Listing Bids',
    )
    def bids(self, request, pk=None):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @bids.mapping.post
    @decorators.permission_classes([permissions.IsAuthenticated])
    def create_bid(self, request, pk=None):
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
        name='Listing Questions',
        pagination_class=None,
    )
    def questions(self, request, pk=None):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @questions.mapping.post
    @decorators.permission_classes([permissions.IsAuthenticated])
    def pub_question(self, request, pk=None):
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
    def watch(self, request, **kwargs):
        listing = generics.get_object_or_404(
            models.Listing, pk=request.data.get('id'))
        watchlist = request.user.watchlist
        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)
        return Response(status=status.HTTP_200_OK)


listing_list_view = ListingViewSet.as_view(
    {'get': 'list'}
)
listing_detail_view = ListingViewSet.as_view(
    {'get': 'retrieve'}
)
listing_create_view = ListingViewSet.as_view(
    {'post': 'create'}
)
listing_bids_view = ListingViewSet.as_view(
    {'get': 'bids', 'post': 'create_bid'}
)
listing_questions_view = ListingViewSet.as_view(
    {'get': 'questions', 'post': 'pub_question'}
)


class BidsViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin):

    queryset = models.Bid.objects.all()
    serializer_class = serializers.BidListSerializer
    permission_classes = (permissions.IsAuthenticated,)


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_classes = {
        'home': serializers.DashboardSerializer,
    }

    def get_queryset(self):
        if self.action == 'home':
            return self.request.user

    @decorators.action(
        detail=False,
        methods=['get'],
        url_path='',
    )
    def home(self, request, **kwargs):
        pass
