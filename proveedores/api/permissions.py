from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff

class IsAuthenticatedNoDelete(BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return False
        else:
            return request.user

class IsAuthenticatedNoEdit(BasePermission):
    def has_permission(self, request, view):
        if request.method == "PATCH" or request.method == "PUT":
            return False
        else:
            return request.user

class IsAuthenticatedNoRead(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return False
        else:
            return request.user