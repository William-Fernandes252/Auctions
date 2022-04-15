from django.urls import path, include
from . import views
from django.contrib.auth import decorators as auth_decorators


urlpatterns = [
    
    # Active Listings view
    path(
        "", 
        views.ListingListView.as_view(), 
        name="index"
    ),
    path(
        "category/<str:category>", 
        views.ListingListView.as_view(), 
        name="category"
    ),
    path(
        "watchlist", 
        auth_decorators.login_required(
            views.ListingListView.as_view(watchlist=True)
        ), 
        name="watchlist"
    ),
    
    # Create listing view
    path("create", views.ListingCreateView.as_view(), name="create"),
    
    # Listing view
    path("listing/<int:pk>", 
        views.ListingDetailsView.as_view(),
        name="listing"
    ),
    path("close/<int:pk>", views.close_listing, name="close"),
    path("bid/<int:pk>", views.bid, name="bid"),
    path("question/<int:pk>", views.add_question, name="question"),
    path("watch/<int:pk>", views.watch, name="watch"),
    
    # API endpoints
    path("api/", include("api.urls"))
    
]