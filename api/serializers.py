from rest_framework import serializers
from auctions.models import Listing, Bid, Question, Answer, Category
from .mixins import ListingSerializerMixin
from rest_framework.exceptions import ValidationError


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
        view_name='listing-details',
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
    ListingSerializerMixin,
    serializers.ModelSerializer):
    
    url = serializers.HyperlinkedIdentityField(
        view_name='listing-details',
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
    ListingSerializerMixin,
    serializers.ModelSerializer):

    category = serializers.SerializerMethodField(read_only=True)
    current_bid = BidAbstractSerializer(source='bids.first')
    all_bids = serializers.HyperlinkedIdentityField(
        view_name = 'listing-bid-list',
        lookup_field = 'pk'
    )
    
    class Meta:
        model = Listing
        fields = [
            'id',
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
    serializers.ModelSerializer,
    ListingSerializerMixin):
    
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
            invalid_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if invalid_keys:
                raise ValidationError(
                    {'details': f'Got unknown field {invalid_keys.pop()}'}
                )
        return data
        
        
class AnswerSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    author = serializers.CharField(source='author.get_full_name', read_only=True)
    
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