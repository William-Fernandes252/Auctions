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
    user_watchlist_api_view,
    user_listing_list_view,
    user_listing_details_view,
)
from auctions.models import Listing, Bid, Question, Category, Answer
from authentication.models import User


API_BASE_URL = "/auctions/api/"


class AuctionsAPITestCase(TestCase):
    
    def setUp(self):
        
        # Set the request factory, authenticated user and anonymous user
        self.factory = APIRequestFactory(enforce_csrf_checks=False)
        self.user = User.objects.create(
            username='tester', 
            password='QWERTY!@#', 
            email='tester.user@email.com',
            first_name='Tester',
            last_name='User',
        )
        self.anonymous = AnonymousUser()
        
        # Set instances of the models
        # Users
        user1 = User.objects.create(
            username='user1', 
            password='QWERTY!@#', 
            email='user1.test@email.com',
            first_name='User',
            last_name='One',
        )
        user2 = User.objects.create(
            username='user2', 
            password='QWERTY!@#', 
            email='user2.test@email.com',
            first_name='User',
            last_name='Two',
        )
        user3 = User.objects.create(
            username='user3', 
            password='QWERTY!@#', 
            email='user1.test@email.com',
            first_name='User',
            last_name='Three',
        )
        
        # Categories
        category1 = Category.objects.create(name='music')
        category2 = Category.objects.create(name='vehicles')
        category3 = Category.objects.create(name='toys')
        
        # Listings
        listing1 = Listing.objects.create(
            author=user1, 
            description="instrument", 
            title="listing1",
            initial_price=2000.00,
            duration=7,
            category=category1
        )
        listing2 = Listing.objects.create(
            author=user2, 
            description="cart", 
            title="listing2",
            initial_price=10000.00,
            duration=14,
            category=category2
        )
        listing3 = Listing.objects.create(
            author=user3, 
            description="action figure", 
            title="listing3",
            initial_price=500.00,
            duration=30,
            category=category3
        )
        
        # Questions
        question1 = Question.objects.create(
            user=user1, 
            listing=listing2, 
            body="This testcase is going to pass?"
        )
        question2 = Question.objects.create(
            user=user2, 
            listing=listing1, 
            body="This testcase is going to pass?"
        )
        question3 = Question.objects.create(
            user=user3, 
            listing=listing1, 
            body="This testcase is going to pass?"
        )
        question4 = Question.objects.create(
            user=user3, 
            listing=listing2, 
            body="This testcase is going to pass?"
        )
        question5 = Question.objects.create(
            user=user1, 
            listing=listing3, 
            body="This testcase is going to pass?"
        )
        
        # Bids
        Bid.objects.create(user=user1, listing=listing2, value=12000)
        Bid.objects.create(user=user2, listing=listing1, value=2500)
        Bid.objects.create(user=user1, listing=listing3, value=600)
        Bid.objects.create(user=user2, listing=listing3, value=700)
        Bid.objects.create(user=user3, listing=listing2, value=14000)
        
        # Answers
        question1.answer = Answer.objects.create(author=user2, body="Probably not...")
        question2.answer = Answer.objects.create(author=user1, body="No.")
        question3.answer = Answer.objects.create(author=user1, body="Nah")
        question4.answer = Answer.objects.create(author=user2, body="YES!")
        
        
    def test_listing_list_view_pagination(self):
        """Test pagination of the data returned from listings list view
        """
        request = self.factory.get(API_BASE_URL + '/listings/')
        request.user = self.anonymous
        response = listing_list_view(request)
        self.assertEqual(response.status_code, 200)
        
        data = response.data
        self.assertEqual(data.get('count'), 3)
        self.assertIsNone(data.get('next'))
        self.assertIsNone(data.get('previous'))
        
        
    def test_listing_list_view_listing_data(self):
        """Test listing data from the listings list view
        """
        request = self.factory.get(API_BASE_URL + '/listings/')
        request.user = self.anonymous
        response = listing_list_view(request)
        
        result = response.data.get('results')[0]
        title = result.get('title')
        current_bid = result.get('current_bid')
        
        self.assertEqual(title, 'listing1')
        self.assertEqual(current_bid.get('value'), '2500.00')
        self.assertEqual(current_bid.get('user'), 'User Two')
        
        
    def test_listing_details_view(self):
        """Test listing data from the listing details view
        """
        request = self.factory.get(API_BASE_URL + '/listings/<int:pk>/')
        request.user = self.anonymous
        response = listing_details_view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        
        listing_data = response.data
        self.assertEqual(listing_data.get('title'), 'listing1')
        self.assertEqual(listing_data.get('id'), 1)
        self.assertEqual(listing_data.get('description'), 'instrument')
        self.assertEqual(listing_data.get('initial_price'), '2000.00')
        self.assertEqual(listing_data.get('category'), 'music')
        
        
    def test_authentication_required_view(self):
        """Check forbidden status code for request without authentication
        """
        request = self.factory.get(API_BASE_URL + '/bids/')
        request.user = self.anonymous
        response = bid_list_view(request)
        self.assertEqual(response.status_code, 403)
        
        
    def test_bid_list_view(self):
        """Test bid data from the bids list view
        """
        request = self.factory.get(API_BASE_URL + '/bids/')
        request.user = self.user
        response = bid_list_view(request)
        self.assertEqual(response.status_code, 200)
        
        data = response.data
        self.assertEqual(data.get('count'), 5)
        
        result = data.get('results')[0]
        self.assertEqual(result.get('value'), '14000.00')
        self.assertEqual(result.get('user'), 'User Three')
        
        listing_data = result.get('listing')
        self.assertEqual(listing_data.get('title'), 'listing2')
        
        
    def test_listing_bid_list_view(self):
        """Test bid data from the listing bids list view
        """
        request = self.factory.get(API_BASE_URL + '/listing/<int:pk>/bids/')
        request.user = self.user
        response = listing_bid_list_view(request, pk=2)
        self.assertEqual(response.status_code, 200)
        
        data = response.data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0].get('value'), '14000.00')
        self.assertEqual(data[0].get('user'), 'User Three')
        
        
    def test_unauthenticated_bid_post(self):
        """Test bid posting with request without authentication
        """
        request = self.factory.post(API_BASE_URL + '/listing/<int:pk>/bids/', {'value': '15000.00'})
        request.user = self.anonymous
        response = listing_bid_list_view(request, pk=2)
        self.assertEqual(response.status_code, 403)
        
        
    def test_authenticated_bid_post(self):
        """Test bid posting with authenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listing/<int:pk>/bids/', 
            {'value': '15000.00'},
            format='json'
        )
        request.user = self.user
        response = listing_bid_list_view(request, pk=2)
        self.assertEqual(response.status_code, 201)
        
        
    def test_unauthenticated_listing_creation(self):
        """Test listing creation with unauthenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listing/create/', 
            {
                'title': 'new_listing',
                'initial_price': 200,
                'duration': 7,
                'category': 1,
                'public': True
            },
            form='json',
        )
        request.user = self.anonymous
        response = listing_create_view(request)
        self.assertEqual(response.status_code, 403)
        
        
    def test_listing_creation_with_invalid_duration(self):
        """Test listing creation with invalid duration
        """
        request = self.factory.post(
            API_BASE_URL + '/listing/create/', 
            {
                'title': 'new_listing',
                'initial_price': 200,
                'duration': 6,
                'category': 1,
                'public': True
            },
            form='json',
        )
        request.user = self.user
        response = listing_create_view(request)
        self.assertEqual(response.status_code, 400)
        
        
    def test_listing_creation_with_invalid_category(self):
        """Test listing creation with invalid category
        """
        request = self.factory.post(
            API_BASE_URL + '/listing/create/', 
            {
                'title': 'new_listing',
                'initial_price': 200,
                'duration': 7,
                'category': 'invalid',
                'public': True
            },
            form='json',
        )
        request.user = self.user
        response = listing_create_view(request)
        self.assertEqual(response.status_code, 400)
        
        
    def test_listing_creation(self):
        """Test listing creation with valid data and authenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listing/create/', 
            {
                'title': 'new_listing',
                'description': 'This listing is valid.',
                'initial_price': 200,
                'duration': 7,
                'category': 2,
                'public': True,
            },
            form='json',
        )
        request.user = self.user
        response = listing_create_view(request)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        
    
    def test_listing_questions_list_view(self):
        """Test questions data from the listing questions list view
        """
        request = self.factory.get(API_BASE_URL + '/')