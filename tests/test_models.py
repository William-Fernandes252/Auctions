from auctions.models import *
from auctions.views import *
from django.test import TestCase


class SetUp(TestCase):
    """Set up for models testcase.
    """
    def setUp(self):
        # Set users
        u1 = User.objects.create(username='user1', email='user1@example.com', password = 'QWERTY!@#', first_name="User", last_name="One")
        u2 = User.objects.create(username='user2', email='user2@example.com', password = 'QWERTY!@#', first_name="User", last_name="Two")
        u3 = User.objects.create(username='user3', email='user3@example.com', password = 'QWERTY!@#', first_name="User", last_name="Three")
        
        # Define categories
        c1 = Category.objects.create(name='c1')
        c2 = Category.objects.create(name='c2')
        c3 = Category.objects.create(name='c3')
        c4 = Category.objects.create(name='c4')
        c5 = Category.objects.create(name='c5')
        
        # Set listings
        l1 = Listing.objects.create(
            author=u1, 
            description="", 
            title="Test 1", 
            initial_price=1000.00, 
            category=c1,
            duration=30
        )   
        l2 = Listing.objects.create(
            author=u2, 
            description="", 
            title="Test 2", 
            initial_price=500.00, 
            category=c2, 
            duration=28
        )
        l3 = Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 3", 
            initial_price=500.00, 
            category=c3, 
            duration=0
        )
        l4 = Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 4", 
            initial_price=0.00, 
            category=c4, 
            duration=7
        )
        l5 = Listing.objects.create(
            author=u3, 
            description="", 
            title="Test 5", 
            initial_price=1.00,
            category=c5, 
            duration=3
        )
        l5.end_time = l5.creation_time
        l5.save()
        
        # Set watchlists
        u2.watchlist.add(l1)
        u1.watchlist.add(l2)
    

class ModelsTestCase(SetUp):
      
    def test_valid_listing(self):
        """Check validation of listings"""
        u = User.objects.get(username='user1')
        l = Listing.objects.get(author=u, title="Test 1")
        self.assertTrue(l.is_valid_listing())
        
        
    def test_invalid_duration(self):
        """Check invalidation of listings due to zero duration"""
        u = User.objects.get(username='user3')
        l = Listing.objects.get(author=u, title="Test 3")
        self.assertFalse(l.is_valid_listing())
        
        
    def test_invalid_price(self):
        """Check invalidation of listings due to invalid price"""
        u = User.objects.get(username='user3')
        l = Listing.objects.get(author=u, title="Test 4")
        self.assertFalse(l.is_valid_listing())
        
        
    def test_invalid_ending(self):
        """Check correction of end time on save"""
        u = User.objects.get(username='user3')
        l = Listing.objects.get(author=u, title="Test 5")
        self.assertTrue(l.is_valid_listing())
        
        
    def test_listings_count(self):
        """Check listings count"""
        self.assertEqual(Listing.objects.count(), 5)
        
        
    def test_listing_watchers(self):
        """Check watchlist functionality"""
        u = User.objects.get(username='user1')
        l = Listing.objects.get(author=u, title="Test 1")
        self.assertEqual(l.watchers.count(), 1)