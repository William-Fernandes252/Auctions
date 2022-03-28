from rest_framework import serializers
from auctions.models import Listing, Bid, Question, Answer, Category
from .mixins import ListingSerializerMixin


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
    )
    
    class Meta:
        model = Listing
        fields = [
            'title',
            'url',
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
    serializers.ModelSerializer,
    ListingSerializerMixin):
    
    url = serializers.HyperlinkedIdentityField(
        view_name='listing-details',
        lookup_field='pk',
    )
    current_bid = BidAbstractSerializer(source='bids.first')
    
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
    serializers.ModelSerializer,
    ListingSerializerMixin):

    category = serializers.SerializerMethodField(read_only=True)
    current_bid = BidAbstractSerializer(source='bids.first')
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'category',
            'initial_price',
            'current_bid',
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
        
        
class ListingEditSerializer(serializers.ModelSerializer):
    close = serializers.BooleanField(source="ended_manually", write_only=True)
    private = serializers.BooleanField(source="public", write_only=True) 
    
    class Meta:
        model = Listing
        fields = ['close', 'private']
        
        
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
        fields = ['body',]
        
        
class QuestionSerializer(serializers.ModelSerializer):
    on = serializers.DateTimeField(source='time', read_only=True)
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    answer = AnswerSerializer(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'user',
            'on',
            'body',
            'answer',
        ]