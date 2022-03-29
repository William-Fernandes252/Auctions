from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser
from api.views import (
    listing_list_view,
    listing_create_view,
    listing_details_view,
    bid_list_view,
    listing_bid_list_view,
    listing_question_list_view,
    answer_question_view,
    watch_listing,
    watchlist_api_view,
    user_listing_list_view,
    user_listing_details_view,
)
from auctions.models import Listing, Bid, Question, Category, Answer
from authentication.models import User


class AuctionsAPITestCase(TestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = user = User.objects.create(
            username='tester', 
            password='QWERTY!@#', 
            email='tester.user@email.com',
            first_name='Tester',
            last_name='User',
        )