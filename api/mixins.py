from auctions.models import Listing
from rest_framework import viewsets


class MultipleSerializersMixin:

    serializer_classes = {
        'default': None,
    }

    def get_serializer_class(self):
        """Instantiates and returns the serializer for the given action.
        """
        return self.serializer_classes.get(
            self.action, self.serializer_classes.get('default'))


class ListingSerializerMixin:
    def get_category(self, obj):
        if not hasattr(obj, 'id') or not isinstance(obj, Listing):
            return None
        return obj.category.name


class ListingQuerysetMixin:
    queryset = Listing.objects.active()

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if q is not None:
            queryset = queryset.search(query=q)
        if category is not None:
            queryset = queryset.from_category(category)
        return queryset


class UserListingsQuerysetMixin(ListingQuerysetMixin):
    queryset = Listing.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)
