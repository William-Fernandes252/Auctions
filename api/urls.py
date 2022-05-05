from django.urls import path
from . import views, viewsets
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'listings', viewsets.ListingViewSet)
router.register(r'bids', viewsets.BidsViewSet)

urlpatterns = [
    path(
        "listings/<int:listing_pk>/questions/<int:question_pk>/answer/", 
        views.answer_question_view, 
        name="answer-question"
    ),
    path(
        "user/", 
        views.user_home_api_view, 
        name="user-home"
    ),
    path(
        "user/watchlist/", 
        views.user_watchlist_api_view, 
        name="listing-watchlist"
    ),
    path(
        "user/listings/", 
        views.user_listing_list_view, 
        name="user-listing-list"
    ),
    path(
        "user/bids/",
        views.user_bid_list_view,
        name="user-bid-list"
    ),
    path(
        "user/listings/<int:pk>/", 
        views.user_listing_details_view, 
        name="user-listing-details"
    ),
] + router.urls