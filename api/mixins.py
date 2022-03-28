from auctions.models import Listing
from rest_framework import serializers


class ListingSerializerMixin:
    def get_category(self, obj):
        if not hasattr(obj, 'id') or not isinstance(obj, Listing):
            return None
        return obj.category.name