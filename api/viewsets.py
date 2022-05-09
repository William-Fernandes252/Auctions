from rest_framework import (
    viewsets,
    mixins,
    decorators,
    status,
    generics,
)
from rest_framework.response import Response
from rest_framework_extensions import mixins as extension_mixins
from . import serializers, permissions as api_permissions
from rest_framework import permissions
from . import mixins as api_mixins
from auctions import models
from authentication import models as auth_models

from django.shortcuts import get_object_or_404


class BidsViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin):

    queryset = models.Bid.objects.all()
    serializer_class = serializers.BidSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ListingViewSet(extension_mixins.DetailSerializerMixin,
                     api_mixins.ListingQuerysetMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    queryset = models.Listing.objects.active()
    queryset_detail = queryset.prefetch_related('bids')
    permission_classes = (api_permissions.ListingPermission,)
    serializer_class = serializers.ListingAbstractSerializer
    serializer_detail_class = serializers.ListingDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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


class ListingBidsViewSet(extension_mixins.NestedViewSetMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         BidsViewSet):

    serializer_class = serializers.BidAbstractSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            listing=models.Listing.objects.get(
                pk=self.kwargs.get('parent_lookup_listing')
            )
        )


class ListingQuestionsViewSet(extension_mixins.NestedViewSetMixin,
                              viewsets.ModelViewSet):

    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    permission_classes = (api_permissions.QuestionPermission,)
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            listing=models.Listing.objects.get(
                pk=self.kwargs.get('parent_lookup_listing')
            )
        )

    @decorators.action(
        detail=True,
        methods=['post'],
        serializer_class=serializers.AnswerSerializer,
        lookup_field='pk',
        lookup_url_kwarg='parent_lookup_listing'
    )
    def answer(self, request, **kwargs):
        question = get_object_or_404(models.Question, pk=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.check_object_permissions(request, question)
        question.answer = serializer.save(author=request.user)
        question.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardViewSet(api_mixins.MultipleSerializersMixin,
                       viewsets.GenericViewSet):

    queryset = auth_models.User.objects.all()
    permission_classes = (api_permissions.DashboardPermission,)
    serializer_classes = {
        'home': serializers.DashboardSerializer,
        'watchlist': serializers.ListingSerializer,
        'wins': serializers.ListingSerializer
    }

    @decorators.action(
        detail=True,
        methods=['get'],
        name="Dashboard Home"
    )
    def home(self, request, **kwargs):
        return Response(self.get_serializer(request.user).data,
                        status=status.HTTP_200_OK)

    @decorators.action(
        detail=True,
        methods=['get'],
    )
    def watchlist(self, request, **kwargs):
        queryset = request.user.watchlist.active()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=True,
        methods=['get']
    )
    def wins(self, request, **kwargs):
        return Response(self.get_serializer(request.user.wins).data,
                        status=status.HTTP_200_OK)


class DashboardListingsViewSet(extension_mixins.NestedViewSetMixin,
                               extension_mixins.DetailSerializerMixin,
                               api_mixins.ListingQuerysetMixin,
                               mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               viewsets.GenericViewSet):

    queryset = models.Listing.objects.all()
    queryset_detail = queryset.prefetch_related('bids')
    permission_classes = (
        api_permissions.DashboardPermission,
        api_permissions.ListingPermission,
    )
    serializer_class = serializers.ListingSerializer
    serializer_detail_class = serializers.ListingUpdateSerializer


class DashboardBidsViewSet(extension_mixins.NestedViewSetMixin,
                           BidsViewSet):
    permission_classes = (api_permissions.DashboardPermission,)
