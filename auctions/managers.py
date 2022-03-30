from django.db import models
from django.db.models import Q
from datetime import datetime


class ListingQuerySet(models.QuerySet):
    def is_public(self):
        return self.filter(public=True)
    
    def search(self, query, user=None):
        lookup = (
            Q(title__icontains=query) |\
            Q(description__icontains=query)
        )
        queryset = self.is_public().filter(lookup)
        if user is not None:
            user_qs = self.filter(user=user)
            queryset = (queryset | user_qs).distinct()
        return queryset
    
    def active(self, user=None):
        queryset = self.is_public().filter(ended_manually=False, end_time__gte=datetime.now())
        if user is not None:   
            user_qs = self.filter(user=user)
            queryset = (queryset | user_qs).distinct()
        return queryset
    
    def from_category(self, category):
        return self.filter(category__name=category)