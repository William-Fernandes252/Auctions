from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_extensions import serializers as extended_serializers
from auctions.models import Listing, Bid, Question, Answer
from authentication.models import User
from . import mixins


class BidAbstractSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='creation_time', read_only=True)
    user = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Bid
        fields = [
            'value',
            'user',
            'on',
        ]


class ListingAbstractSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='listing-detail',
        lookup_field='pk',
        read_only=True
    )
    current_bid = BidAbstractSerializer(source='bids.first', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'title',
            'current_bid',
            'url',
            'end_time',
        ]


class BidListSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='creation_time', read_only=True)
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    listing = ListingAbstractSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = [
            'listing',
            'user',
            'value',
            'on',
        ]


class ListingListSerializer(
        mixins.ListingSerializerMixin,
        serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='listing-detail',
        lookup_field='pk',
    )
    current_bid = BidAbstractSerializer(source='bids.first', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'current_bid',
            'end_time',
            'url',
        ]


class ListingDetailsSerializer(
        mixins.ListingSerializerMixin,
        serializers.ModelSerializer):

    author = serializers.CharField(
        source='author.get_full_name', read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    current_bid = BidAbstractSerializer(source='bids.first')
    all_bids = serializers.HyperlinkedIdentityField(
        view_name='listing-bids',
        lookup_field='pk'
    )

    class Meta:
        model = Listing
        fields = [
            'id',
            'author',
            'title',
            'description',
            'category',
            'initial_price',
            'current_bid',
            'all_bids',
            'creation_time',
            'end_time',
            'public',
        ]


class ListingCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'category',
            'initial_price',
            'duration',
            'public',
        ]


class ListingEditSerializer(
        extended_serializers.PartialUpdateSerializerMixin,
        serializers.ModelSerializer,
        mixins.ListingSerializerMixin):

    category = serializers.SerializerMethodField(read_only=True)
    ended = serializers.BooleanField(source='ended_manually')
    bids = BidAbstractSerializer(read_only=True, many=True)

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'category',
            'initial_price',
            'bids',
            'creation_time',
            'end_time',
            'ended',
            'public',
        ]
        read_only_fields = list(
            filter(
                lambda field: field != 'public' and field != 'ended',
                fields
            )
        )

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            invalid_keys = set(self.initial_data.keys()) - \
                set(self.fields.keys())
            if invalid_keys:
                raise ValidationError(
                    {'details': f'Got unknown field {invalid_keys.pop()}'}
                )
        return data


class AnswerSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    author = serializers.CharField(
        source='author.get_full_name', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'author',
            'on',
            'body',
        ]


class AnswerCreationSerializer(serializers.ModelSerializer):
    body = serializers.CharField(write_only=True)

    class Meta:
        model = Answer
        fields = ['body']


class QuestionSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'user',
            'on',
            'body',
            'answer',
        ]


class DashboardSerializer(serializers.HyperlinkedModelSerializer):
    listings_count = serializers.SerializerMethodField()
    bids_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'listings_count',
            'listings',
            'bids_count',
            'bids',
            'wins',
            'questions',
            'watchlist',
        ]
        read_only_fields = fields
        extra_kwargs = {
            'listings': {'view_name': 'dashboard-listings-list'},
            'bids': {'view_name': 'dashboard-bids-list'},
            'wins': {'view_name': 'dashboard-wins'},
            'questions': {'view_name': 'dashboard-questions'},
            'watchlist': {'view_name': 'dashboard-watchlist'},
        }

    def get_listings_count(self, obj):
        return obj.listings.count()

    def get_bids_count(self, obj):
        return obj.bids.count()
