from auctions import models
from authentication import models as auth_models
from rest_framework import permissions


class MultipleSerializersMixin:

    serializer_classes = {
        'default': None,
    }

    def get_serializer_class(self):
        """Instantiates and returns the serializer for the given action.
        """
        return self.serializer_classes.get(
            self.action, self.serializer_class)


class ListingSerializerMixin:
    def get_category(self, obj):
        if not hasattr(obj, 'id') or not isinstance(obj, models.Listing):
            return None
        return obj.category.name


class ListingQuerysetMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            q = self.request.GET.get('q')
            if q is not None:
                queryset = queryset.search(query=q)
            category = self.request.GET.get('category')
            if category is not None:
                queryset = queryset.from_category(category)
        return queryset
