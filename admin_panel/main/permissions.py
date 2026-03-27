from requests import Response
from rest_framework.permissions import BasePermission
from .models import *
class Dynamicpermission(BasePermission):
    def has_permission(self, request,view):
        if not request.user:
            return False

        user = request.user
        print('user:', user)

        role_obj = RoleUser.objects.filter(user=user).first()
        rolename = role_obj.role.rolename
        if not role_obj:
            print("No role assigned")
            return False

        print('rolename:',rolename)

        per=[]
        x = RolePermission.objects.filter(role=role_obj.role)
        for i in x:
            per.append(i.permission.permission_name)
            print(i.permission.permission_name)

        print("Permissions for the role:", per)

        if rolename == 'User':
            return request.method in per
        if rolename == 'Viewer':
            return request.method in per
        if rolename == 'Manager':
            return request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        return False
    


class Assignedpermissionset(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        role_obj = RoleUser.objects.filter(user=user).first()
        if not role_obj:
            return False

        rolename = role_obj.role.rolename
        print('rolename: ', rolename)
        if rolename == 'User':
            self.message = "Not permission to access"
            return False
        elif rolename == 'Manager':
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']
        return False
    


class IsAdminOrManager(BasePermission):
    def has_permission(self, request,view):
        user = request.user

        if not user:
            return False

        try:
            role_user = RoleUser.objects.get(user_id=user.id)
        except RoleUser.DoesNotExist:
            self.message = "User does not have an assigned role."
            return False

        if role_user.role.rolename in ['Admin', 'Manager']:
            return True

        return False
    

class Orderpermission(BasePermission):
    def has_permission(self, request,view):
        user = request.user

        if not user:
            return False

        try:
            role_user = RoleUser.objects.get(user_id=user.id)
        except RoleUser.DoesNotExist:
            self.message = "User does not have an assigned role."
            return False
        rolename = role_user.role.rolename

        if rolename == 'User':
            return request.method in ['GET', 'POST']
        elif rolename == 'Manager':
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']
        return False 