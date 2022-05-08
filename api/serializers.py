from rest_framework import serializers, exceptions, relations, reverse as uri
from rest_framework_extensions import serializers as extended_serializers
from auctions import models
from authentication import models as auth_models, serializers as auth_serializers
from . import mixins


class ParameterisedHyperlinkedIdentityField(
        relations.HyperlinkedIdentityField):
    """
    Represents the instance, or a property on the instance, using
    hyperlinking.

    lookup_fields is a tuple of tuples of the form: 
    ('model_field', 'url_param')
    """
    lookup_fields = (('pk', 'pk'),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', self.lookup_fields)
        return super().__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            attr = obj
            for field in model_field.split('.'):
                attr = getattr(attr, field)
            kwargs[url_param] = attr
        return uri.reverse(view_name,
                           kwargs=kwargs,
                           request=request,
                           format=format)


class BidAbstractSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='creation_time', read_only=True)
    user = auth_serializers.UserSerializer(read_only=True)

    class Meta:
        model = models.Bid
        fields = [
            'value',
            'user',
            'on',
        ]


class ListingAbstractSerializer(serializers.ModelSerializer,
                                mixins.MultipleSerializersMixin):

    url = serializers.HyperlinkedIdentityField(
        view_name='listing-detail',
        lookup_field='pk',
        read_only=True
    )
    current_bid = BidAbstractSerializer(source='bids.first', read_only=True)

    class Meta:
        model = models.Listing
        fields = [
            'title',
            'description',
            'category',
            'initial_price',
            'duration',
            'public',
            'current_bid',
            'url',
            'end_time',
        ]
        extra_kwargs = {
            'duration': {'write_only': True},
            'end_time': {'read_only': True}
        }


class BidSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='creation_time', read_only=True)
    user = auth_serializers.UserSerializer(read_only=True)
    listing = ListingAbstractSerializer(read_only=True)

    class Meta:
        model = models.Bid
        fields = [
            'listing',
            'user',
            'value',
            'on',
        ]


class ListingSerializer(
        mixins.ListingSerializerMixin,
        serializers.ModelSerializer):

    url = ParameterisedHyperlinkedIdentityField(
        view_name='dashboard-listings-detail',
        lookup_fields=(('author.pk', 'parent_lookup_author'), ('pk', 'pk')),
    )
    current_bid = BidAbstractSerializer(source='bids.first', read_only=True)

    class Meta:
        model = models.Listing
        fields = [
            'id',
            'title',
            'description',
            'current_bid',
            'end_time',
            'url',
        ]


class ListingDetailSerializer(
        mixins.ListingSerializerMixin,
        serializers.ModelSerializer):

    author = auth_serializers.UserSerializer(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    current_bid = BidAbstractSerializer(source='bids.first')
    all_bids = serializers.HyperlinkedIdentityField(
        view_name='listing-bids-list',
        lookup_field='pk',
        lookup_url_kwarg='parent_lookup_listing'
    )

    class Meta:
        model = models.Listing
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
        ]
        read_only_fields = ['id', 'author', 'creation_time', 'end_time']


class ListingUpdateSerializer(
        extended_serializers.PartialUpdateSerializerMixin,
        serializers.ModelSerializer,
        mixins.ListingSerializerMixin):

    category = serializers.SerializerMethodField(read_only=True)
    ended = serializers.BooleanField(source='ended_manually')
    bids = BidAbstractSerializer(read_only=True, many=True)

    class Meta:
        model = models.Listing
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
                raise exceptions.ValidationError(
                    {'details': f'Got unknown field {invalid_keys.pop()}'}
                )
        return data


class AnswerSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    author = auth_serializers.UserSerializer(read_only=True)

    class Meta:
        model = models.Answer
        fields = [
            'author',
            'on',
            'body',
        ]


class AnswerCreationSerializer(serializers.ModelSerializer):
    body = serializers.CharField(write_only=True)

    class Meta:
        model = models.Answer
        fields = ['body']


class QuestionSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = models.Question
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
        model = auth_models.User
        fields = [
            'listings_count',
            'listings',
            'bids_count',
            'bids',
            'wins',
            'watchlist',
        ]
        read_only_fields = fields
        extra_kwargs = {
            'listings': {
                'view_name': 'dashboard-listings-list',
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'parent_lookup_author'
            },
            'bids': {
                'view_name': 'dashboard-bids-list',
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'parent_lookup_user'
            },
            'wins': {'view_name': 'dashboard-wins'},
            'watchlist': {'view_name': 'dashboard-watchlist'},
        }

    def get_listings_count(self, obj):
        return obj.listings.count()

    def get_bids_count(self, obj):
        return obj.bids.count()
