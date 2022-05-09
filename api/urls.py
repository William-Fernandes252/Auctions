from . import viewsets
from rest_framework_extensions import routers


router = routers.ExtendedDefaultRouter()
router.register(r'bids', viewsets.BidsViewSet)

listing_router = router.register(r'listings', viewsets.ListingViewSet)
listing_router.register(r'bids',
                        viewsets.ListingBidsViewSet,
                        basename='listing-bids',
                        parents_query_lookups=['listing'])
listing_router.register(r'questions',
                        viewsets.ListingQuestionsViewSet,
                        basename='listing-questions',
                        parents_query_lookups=['listing'])

dashboard_router = router.register(r'dashboard',
                                   viewsets.DashboardViewSet,
                                   basename='dashboard')
dashboard_router.register(r'listings',
                          viewsets.DashboardListingsViewSet,
                          basename='dashboard-listings',
                          parents_query_lookups=['author'])
dashboard_router.register(r'bids',
                          viewsets.DashboardBidsViewSet,
                          basename='dashboard-bids',
                          parents_query_lookups=['user'])

urlpatterns = router.urls
