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
