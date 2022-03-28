from django.urls import path
from . import views


urlpatterns = [
    path("", views.api_home, name="home"),
    path("listings/", views.listing_list_view, name="listing-list"),
    path("listings/create/", views.listing_create_view, name="listing-create"),
    path("listings/<int:pk>/", views.listing_details_view, name="listing-details"),
    path("bids/", views.bid_list_view, name="bid-list"),
    path("listings/<int:pk>/bids/", views.listing_bid_list_view, name="listing-bid-list"),
    path(
        "listings/<int:pk>/questions/", 
        views.listing_question_list_view, 
        name="listing-question-list"    
    ),
    path(
        "listings/<int:listing_pk>/questions/<int:question_pk>/answer/", 
        views.answer_question_view, 
        name="answer-question"
    ),
    path("listings/watch/", views.watch_listing, name="watch-listing"),
    path("user/watchlist/", views.watchlist_api_view, name="listing-watchlist"),
    path("user/listings/", views.user_listings_view, name="user-listings"),
]