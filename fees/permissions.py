from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """Check if user is authenticated"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsSchoolOwnerOrReadOnly(BasePermission):
    """Check if user belongs to the same school"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'school')
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Check if object has school attribute
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        
        return True
