from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.role == "Manager"


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.role == "User"


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.role == "Viewer"
    

class CategoryPermission(BasePermission):
    def hash_permission(self,request):
        role = request.user.role.role

        if role == "Manager":
            return True

        if role == "User":
            return request.method in ["GET"]

        if role == "Viewer":
            return request.method == "GET"

        return False

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        role = request.user.role.role

        if role == "Manager":
            return True

        if role == "User":
            return request.method in ["GET"]

        if role == "Viewer":
            return request.method == "GET"

        return False
    
class OrderPermission(BasePermission):
    def has_permission(self, request, view):
        role = request.user.role.role

        if role == "Manager":
            return True
        elif role == "User":
            return request.method in ["GET","POST"]
        elif role == "Viewer":
            return request.method == "GET"
        return False
    
class OrderDetailsPermission(BasePermission):
    def has_permission(self, request, view):
        role = request.user.role.role

        if role == "Manager":
            return True
        elif role == "User":
            return request.method in ["GET"]
        elif role == "Viewer":
            return False
        return False
    