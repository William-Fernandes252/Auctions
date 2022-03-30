from django.test import Client
from django.db.models import Max
from auctions.models import *
from auctions.views import *
from .test_models import SetUp


class TemplateTestCase(SetUp):

    def test_index(self):
        """Check index page"""
        c = Client()
        response = c.get("/auctions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["listings"]), 5)
            
            
    def test_invalid_listing_page(self):
        """Check invalid listing page"""
        max_id = Listing.objects.all().aggregate(Max("id"))["id__max"]
        c = Client()
        response = c.get(f"listings/{max_id + 1}")
        self.assertEqual(response.status_code, 404)