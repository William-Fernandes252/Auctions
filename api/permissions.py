from rest_framework import permissions


class ListingPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            view.action in ('update', 'partial_update') and
            request.user == obj.author
        )


class QuestionPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            view.action in ('update', 'partial_update') and
            request.user == obj.user
        ) or bool(
            view.action == 'answer' and
            request.user == obj.listing.author
        )


class DashboardPermission(permissions.IsAuthenticated):
    message = "Access to others dashboards is not allowed."

    def has_permission(self, request, view):
        action = view.action
        if bool(action == 'home' or
                action == 'watchlist' or
                action == 'wins'):
            user_id = view.kwargs.get('pk')
        elif view.basename == 'dashboard-listings':
            user_id = view.kwargs.get('parent_lookup_author')
        else:
            user_id = view.kwargs.get('parent_lookup_user')
        return bool(
            super().has_permission(request, view) and
            str(request.user.id) == user_id
        )
