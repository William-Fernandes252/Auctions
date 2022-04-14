from django.urls import path, include
from . import views


urlpatterns = [
    
    # Active Listings view
    path("", views.ListingListView.as_view(), name="index"),
    path("category/<str:category>", views.ListingListView.as_view(), name="category"),
    path("watchlist", views.ListingListView.as_view(watchlist=True), name="watchlist"),
    path("search", views.ListingListView.as_view(), name="search"),
    
    # Create listing view
    path("create", views.create_listing, name="create"),
    
    # Listing view
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("close/<int:listing_id>", views.close_listing, name="close"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("question/<int:listing_id>", views.add_question, name="question"),
    path("watch/<int:listing_id>", views.watch, name="watch"),
    
    # API endpoints
    path("api/", include("api.urls"))
    
]
