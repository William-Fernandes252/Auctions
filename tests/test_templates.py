from django import test
from django.db.models import Max
from auctions import models, views
from authentication import models as auth_models


class SetUp(test.TestCase):
    """Setup for templates testcase
    """
    def setUp(self):
    # Set users
        u1 = auth_models.User.objects.create(username='user1', email='user1@example.com', password = 'QWERTY!@#', first_name="User", last_name="One")
        u2 = auth_models.User.objects.create(username='user2', email='user2@example.com', password = 'QWERTY!@#', first_name="User", last_name="Two")
        u3 = auth_models.User.objects.create(username='user3', email='user3@example.com', password = 'QWERTY!@#', first_name="User", last_name="Three")
        
        # Define categories
        c1 = models.Category.objects.create(name='c1')
        c2 = models.Category.objects.create(name='c2')
        c3 = models.Category.objects.create(name='c3')
        c4 = models.Category.objects.create(name='c4')
        c5 = models.Category.objects.create(name='c5')
        
        # Set listings
        l1 = models.Listing.objects.create(
            author=u1, 
            description="", 
            title="Test 1", 
            initial_price=1000.00, 
            category=c1, 
            duration=14
        )        
        l2 = models.Listing.objects.create(
            author=u2, 
            description="", 
            title="Test 2", 
            initial_price=500.00, 
            category=c2, 
            duration=14
        )
        l3 = models.Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 3", 
            initial_price=500.00, 
            category=c3, 
            duration=7
        )
        l4 = models.Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 4", 
            initial_price=400.00, 
            category=c4, 
            duration=7
        )
        l5 = models.Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 5", 
            initial_price=10000.00,
            category=c5, 
            duration=3
        )
        
        # Set bids
        models.Bid.objects.create(listing=l5, user=u1, value=11000.00)
        models.Bid.objects.create(listing=l4, user=u2, value=500.00)
        models.Bid.objects.create(listing=l3, user=u2, value=550.00)
        models.Bid.objects.create(listing=l2, user=u1, value=600.00)
        models.Bid.objects.create(listing=l1, user=u3, value=1500.00)
        models.Bid.objects.create(listing=l2, user=u3, value=12000.00)
        models.Bid.objects.create(listing=l1, user=u2, value=2000.00)
        
        # Set watchlists
        u2.watchlist.add(l1)
        u1.watchlist.add(l2)
        u3.watchlist.add(l2)
        u1.watchlist.add(l5)


class TemplateTestCase(SetUp):

    def test_index(self):
        """Check index page"""
        c = test.Client()
        response = c.get("/auctions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["listings"]), 5)
            
            
    def test_invalid_listing_page(self):
        """Check invalid listing page"""
        max_id = models.Listing.objects.all().aggregate(Max("id"))["id__max"]
        c = test.Client()
        response = c.get(f"listings/{max_id + 1}")
        self.assertEqual(response.status_code, 404)