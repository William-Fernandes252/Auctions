from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import AnonymousUser
from api import views, viewsets
from auctions import models
from authentication import models as auth_models


API_BASE_URL = "/auctions/api"


class SetUp(TestCase):

    def setUp(self):
        """Setup for test the auctions API endpoints
        """
        # Set the request factory, HTTP client, authenticated user and anonymous user
        self.factory = APIRequestFactory(enforce_csrf_checks=False)
        self.client = APIClient(enforce_csrf_checks=False)
        self.user = auth_models.User.objects.create(
            username='tester',
            email='tester.user@email.com',
            first_name='Tester',
            last_name='User',
        )
        self.user.set_password('QWERTY!@#')
        self.user.save()
        self.anonymous = AnonymousUser()

        # Set instances of the models
        # Users
        user1 = auth_models.User.objects.create(
            username='user1',
            password='QWERTY!@#',
            email='user1.test@email.com',
            first_name='User',
            last_name='One',
        )
        user2 = auth_models.User.objects.create(
            username='user2',
            password='QWERTY!@#',
            email='user2.test@email.com',
            first_name='User',
            last_name='Two',
        )
        user3 = auth_models.User.objects.create(
            username='user3',
            password='QWERTY!@#',
            email='user1.test@email.com',
            first_name='User',
            last_name='Three',
        )

        # Categories
        category1 = models.Category.objects.create(name='music')
        category2 = models.Category.objects.create(name='vehicles')
        category3 = models.Category.objects.create(name='toys')

        # Listings
        listing1 = models.Listing.objects.create(
            author=user1,
            description="instrument",
            title="listing1",
            initial_price=2000.00,
            duration=7,
            category=category1
        )
        listing2 = models.Listing.objects.create(
            author=user2,
            description="cart",
            title="listing2",
            initial_price=10000.00,
            duration=14,
            category=category2
        )
        listing3 = models.Listing.objects.create(
            author=user3,
            description="action figure",
            title="listing3",
            initial_price=500.00,
            duration=30,
            category=category3
        )
        listing4 = models.Listing.objects.create(
            author=self.user,
            description="my listing",
            title="listing4",
            initial_price=9999.99,
            duration=14,
            category=category1
        )

        # Questions
        question1 = models.Question.objects.create(
            user=user1,
            listing=listing2,
            body="This testcase is going to pass?"
        )
        question2 = models.Question.objects.create(
            user=user2,
            listing=listing1,
            body="This testcase is going to pass?"
        )
        question3 = models.Question.objects.create(
            user=user3,
            listing=listing1,
            body="This testcase is going to pass?"
        )
        question4 = models.Question.objects.create(
            user=user3,
            listing=listing2,
            body="This testcase is going to pass?"
        )
        question5 = models.Question.objects.create(
            user=user1,
            listing=listing3,
            body="This testcase is going to pass?"
        )

        # Bids
        models.Bid.objects.create(user=user1, listing=listing2, value=12000)
        models.Bid.objects.create(user=user2, listing=listing1, value=2500)
        models.Bid.objects.create(user=user1, listing=listing3, value=600)
        models.Bid.objects.create(user=user2, listing=listing3, value=700)
        models.Bid.objects.create(user=user3, listing=listing2, value=14000)
        models.Bid.objects.create(user=user3, listing=listing4, value=10000.00)
        models.Bid.objects.create(
            user=self.user, listing=listing1, value=3000.00)

        # Answers
        question1.answer = models.Answer.objects.create(
            author=user2, body="Probably not...")
        question2.answer = models.Answer.objects.create(
            author=user1, body="No.")
        question3.answer = models.Answer.objects.create(
            author=user1, body="Nah")
        question4.answer = models.Answer.objects.create(
            author=user2, body="YES!")

        # Watchlist
        self.user.watchlist.add(listing1)
        self.user.watchlist.add(listing2)


class AuctionsAPITestCase(SetUp):

    def test_listing_list_view_pagination(self):
        """Test pagination of the data returned from listings list view
        """
        request = self.factory.get(API_BASE_URL + '/listings/')
        request.user = self.anonymous
        response = viewsets.listing_list_view(request)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(data.get('count'), 4)
        self.assertIsNone(data.get('next'))
        self.assertIsNone(data.get('previous'))

    def test_listing_list_view_listing_data(self):
        """Test listing data from the listings list view
        """
        request = self.factory.get(API_BASE_URL + '/listings/')
        request.user = self.anonymous
        response = viewsets.listing_list_view(request)

        result = response.data.get('results')[0]
        title = result.get('title')
        current_bid = result.get('current_bid')

        self.assertEqual(title, 'listing1')
        self.assertEqual(current_bid.get('value'), '3000.00')
        self.assertEqual(current_bid.get('user'), 'Tester User')

    def test_listing_search(self):
        """Test listings list endpoint data from a parameterized request
        """
        request = self.factory.get(
            API_BASE_URL + '/listings/',
            {'q': '2', 'category': 'vehicles'}
        )
        request.user = self.anonymous
        response = viewsets.listing_list_view(request)

        data = response.data
        self.assertEqual(data.get('count'), 1)

        result = data.get('results')[0]
        title = result.get('title')
        current_bid = result.get('current_bid')

        self.assertEqual(title, 'listing2')
        self.assertEqual(current_bid.get('value'), '14000.00')
        self.assertEqual(current_bid.get('user'), 'User Three')

    def test_listing_details_view(self):
        """Test listing data from the listing details view
        """
        request = self.factory.get(API_BASE_URL + '/listings/<int:pk>/')
        request.user = self.anonymous
        response = viewsets.listing_detail_view(request, pk=1)
        self.assertEqual(response.status_code, 200)

        listing_data = response.data
        self.assertEqual(listing_data.get('title'), 'listing1')
        self.assertEqual(listing_data.get('id'), 1)
        self.assertEqual(listing_data.get('description'), 'instrument')
        self.assertEqual(listing_data.get('initial_price'), '2000.00')
        self.assertEqual(listing_data.get('category'), 'music')


class UnauthorizedRequestsTestCase(SetUp):

    def test_unauthenticated_bids_list_request(self):
        """Check forbidden status code for request without authentication
        """
        request = self.factory.get(API_BASE_URL + '/bids/')
        request.user = self.anonymous
        response = views.bid_list_view(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_listing_creation(self):
        """Test listing creation with unauthenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/create/',
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
        response = viewsets.listing_create_view(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_bid_post(self):
        """Test bid posting with unauthenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/<int:pk>/bids_create/',
            {'value': '15000.00'},
            format='json'
        )
        request.user = self.anonymous
        response = viewsets.listing_bids_view(request, pk=2)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_question_post(self):
        """Test question post from unauthenticated request
        """
        request = self.factory.post(
            API_BASE_URL + 'listings/<int:pk>/questions_create/',
            {'body': 'Can I make a question?'},
            format='json'
        )
        request.user = self.anonymous
        response = viewsets.listing_questions_view(request, pk=3)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_answer_post(self):
        """Test answer post from unauthenticated request
        """
        request = self.factory.post(
            API_BASE_URL +
            'listings/<int:listing_pk>/questions_list/<int:question_pk>/answer/',
            {'body': 'Yes.'},
            format='json'
        )
        request.user = self.anonymous
        response = views.answer_question_view(
            request, listing_pk=2, question_pk=4)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_watchlist_access(self):
        """Test watchlist access with an unauthenticated request
        """
        request = self.factory.get(API_BASE_URL + 'user/watchlist/')
        request.user = self.anonymous
        response = views.user_watchlist_api_view(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_watch_post(self):
        """Test an unauthenticated post to the watch listing endpoint
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/watch/',
            {'id': 3}
        )
        request.user = self.anonymous
        response = views.watch_listing(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_listing_list_view(self):
        """Test unauthenticated user listings list endpoint request
        """
        request = self.factory.get(API_BASE_URL + 'user/listings/')
        request.user = self.anonymous
        response = views.user_listing_list_view(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_bid_list_view(self):
        """Test unauthenticated user bids list endpoint request
        """
        request = self.factory.get(API_BASE_URL + 'user/bids/')
        request.user = self.anonymous
        response = views.user_bid_list_view(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_listing_details_view(self):
        """Test unauthenticated user listing details endpoint request
        """
        request = self.factory.get(API_BASE_URL + 'user/listings/<int:pk>')
        request.user = self.anonymous
        response = views.user_listing_details_view(request, pk=1)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_edit_listing_view(self):
        """Test unauthenticated edit listing endpoint request
        """
        request = self.factory.put(
            API_BASE_URL + 'user/listings/<int:pk>/',
            {'public': False, 'ended': False},
        )
        request.user = self.anonymous
        response = views.user_listing_details_view(request, pk=4)
        self.assertEqual(response.status_code, 403)


class AutheticatedRequestsTestCase(SetUp):

    def test_bid_list_view(self):
        """Test bid data from the bids list view
        """
        request = self.factory.get(API_BASE_URL + '/bids/')
        request.user = self.user
        response = views.bid_list_view(request)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(data.get('count'), 7)

        result = data.get('results')[0]
        self.assertEqual(result.get('value'), '14000.00')
        self.assertEqual(result.get('user'), 'User Three')

        listing_data = result.get('listing')
        self.assertEqual(listing_data.get('title'), 'listing2')

    def test_listing_bid_list_view(self):
        """Test bid data from the listing bids list view
        """
        request = self.factory.get(
            API_BASE_URL + '/listings/<int:pk>/bids_list/')
        request.user = self.user
        response = viewsets.listing_bids_view(request, pk=2)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0].get('value'), '14000.00')
        self.assertEqual(data[0].get('user'), 'User Three')

    def test_bid_post(self):
        """Test bid posting with authenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/<int:pk>/bids_create/',
            {'value': '15000.00'},
            format='json'
        )
        request.user = self.user
        response = viewsets.listing_bids_view(request, pk=2)
        self.assertEqual(response.status_code, 201)

    def test_listing_creation_with_invalid_duration(self):
        """Test listing creation with invalid duration
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/create/',
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
        response = viewsets.listing_create_view(request)
        self.assertEqual(response.status_code, 400)

    def test_listing_creation_with_invalid_category(self):
        """Test listing creation with invalid category
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/create/',
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
        response = viewsets.listing_create_view(request)
        self.assertEqual(response.status_code, 400)

    def test_listing_creation(self):
        """Test listing creation with valid data and authenticated user
        """
        request = self.factory.post(
            API_BASE_URL + '/listings/create/',
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
        response = viewsets.listing_create_view(request)
        self.assertEqual(response.status_code, 201)

    def test_listing_questions_list_view(self):
        """Test questions data from the listing questions list view
        """
        request = self.factory.get(
            API_BASE_URL + 'listings/<int:pk>/questions_list/')
        request.user = self.anonymous
        response = viewsets.listing_questions_view(request, pk=3)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(len(data), 1)

        question = data[0]
        self.assertEqual(question.get('id'), 5)
        self.assertEqual(question.get('user'), 'User One')
        self.assertEqual(question.get('body'),
                         'This testcase is going to pass?')

    def test_question_post(self):
        """Test question post from authenticated request
        """
        request = self.factory.post(
            API_BASE_URL + 'listings/<int:pk>/questions_create/',
            {'body': 'Can I make a question?'},
            format='json'
        )
        request.user = self.user
        response = viewsets.listing_questions_view(request, pk=2)
        self.assertEqual(response.status_code, 201)

    def test_unauthorized_answer_post(self):
        """Test answer post by an unauthorized user 
        (i.e., a user that is not the author of the listing) 
        """
        request = self.factory.post(
            API_BASE_URL +
            'listings/<int:listing_pk>/questions_list/<int:question_pk>/answer/',
            {'body': 'Yes.'},
            format='json'
        )
        request.user = self.user
        response = views.answer_question_view(
            request, listing_pk=2, question_pk=4)
        self.assertEqual(response.status_code, 403)

    def test_authorized_answer_post(self):
        """Test answer post by the author of the listing 
        """
        request = self.factory.post(
            API_BASE_URL +
            'listings/<int:listing_pk>/questions_list/<int:question_pk>/answer/',
            {'body': 'Yes.'},
            format='json'
        )
        author = models.Listing.objects.get(pk=2).author
        request.user = author
        response = views.answer_question_view(
            request, listing_pk=2, question_pk=4)
        self.assertEqual(response.status_code, 201)

    def test_user_listing_list_view(self):
        """Test user listings list endpoint
        """
        request = self.factory.get(API_BASE_URL + 'user/listings/')
        request.user = self.user
        response = views.user_listing_list_view(request)

        data = response.data
        self.assertEqual(data.get('count'), 1)

        results = data.get('results')
        self.assertEqual(results[0].get('title'), 'listing4')

    def test_user_bid_list_view(self):
        """Test user listings list endpoint
        """
        request = self.factory.get(API_BASE_URL + 'user/listings/')
        request.user = self.user
        response = views.user_bid_list_view(request)

        data = response.data
        self.assertEqual(data.get('count'), 1)

        results = data.get('results')
        self.assertEqual(results[0].get('value'), '3000.00')

    def test_user_listing_details_view(self):
        """Test user listing details endpoint data
        """
        request = self.factory.get(API_BASE_URL + 'user/listings/<int:pk>/')
        request.user = self.user
        response = views.user_listing_details_view(request, pk=4)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(data.get('title'), 'listing4')
        self.assertEqual(len(data.get('bids')), 1)

    def test_invalid_edit_listing_view(self):
        """Test invalid edit listing endpoint request
        """
        request = self.factory.put(
            API_BASE_URL + 'user/listings/<int:pk>/',
            {'close': 'yes'},
        )
        request.user = self.user
        response = views.user_listing_details_view(request, pk=4)
        self.assertEqual(response.status_code, 400)

    def test_edit_listing_view(self):
        """Test edit listing endpoint request
        """
        request = self.factory.put(
            API_BASE_URL + 'user/listings/<int:pk>/',
            {'public': False},
        )
        request.user = self.user
        response = views.user_listing_details_view(request, pk=4)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_edit_listing_view(self):
        """Test unauthorized edit listing endpoint request (i.e., a user trying to edit a listing of another user)
        """
        request = self.factory.put(
            API_BASE_URL + 'user/listings/<int:pk>/',
            {'public': False},
        )
        request.user = auth_models.User.objects.get(username='user2')
        response = views.user_listing_details_view(request, pk=4)
        self.assertEqual(response.status_code, 404)

    def test_watchlist_data(self):
        """Test watchlist access with an authenticated user
        """
        request = self.factory.get(API_BASE_URL + 'user/watchlist/')
        request.user = self.user
        response = views.user_watchlist_api_view(request)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(data.get('count'), 2)

        results = data.get('results')
        self.assertEqual(results[0].get('id'), 1)
        self.assertEqual(results[1].get('id'), 2)

    def test_watch_post(self):
        """Test an authenticated watch post to the watch listing endpoint
        """
        self.client.login(username='tester', password='QWERTY!@#')
        response = self.client.post(
            API_BASE_URL + '/listings/watch/',
            {'id': 3}
        )
        self.assertEqual(response.status_code, 200)


class ViewSetsTestCase(SetUp):

    def test_bids_get_action(self):
        """Test the bids action from the listings viewset with a get request
        """
        response = self.client.get(API_BASE_URL + '/listings/2/bids/')
        self.assertEqual(response.status_code, 200)

    def test_bids_post_action(self):
        """Test the bids action from the listings viewset with a post request
        """
        if self.client.login(username='tester', password='QWERTY!@#'):
            response = self.client.post(
                API_BASE_URL + '/listings/2/bids/',
                {'value': '15000.00'},
                format='json'
            )
            self.assertEqual(response.status_code, 201)
        else:
            raise AssertionError('Login failed')
