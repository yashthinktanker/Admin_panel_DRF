from rest_framework import serializers
from .models import *
from rest_framework.response import Response

class Registerserilizer(serializers.ModelSerializer):
  
    class Meta:
        model = Register
        fields = ['id','username','email','gender']

class Roleseri(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ['is_delete']
        # fields = '__all__'

    def validate_rolename(self,data):
        if not data[0].isupper():
            raise serializers.ValidationError("First letter is upper.")

        if Role.objects.filter(rolename__iexact=data).exists():
            raise serializers.ValidationError("Role already exists.")
        return data
    
    
class Permissionseri(serializers.ModelSerializer):
    class Meta:
        model = Permission
        # fields = '__all__'
        exclude = ['is_delete']

    def validate_permission_name(self, data):
        allowed = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

        if data.upper() not in allowed:
            raise serializers.ValidationError("Invalid permission name.")

        if Permission.objects.filter(permission_name=data.upper()).exists():
            raise serializers.ValidationError("Permission already exists.")

        return data
class Roleserilizer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Register.objects.all())
    class Meta:
        model = RoleUser
        fields = '__all__'

class Categoryserilizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['is_delete']

        def validate_category_name(self, data):
            if Category.objects.filter(category_name__iexact=data).exists():
                raise serializers.ValidationError("Category already exists.")
            return data


class Productserilizer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Product
        exclude = ['is_delete']
        # fields = '__all__'
 


    def validate(self, data):
        if Product.objects.filter(category=data['category'], product_name__iexact=data['product_name']).exists():
            raise serializers.ValidationError("Product with this name already exists.") 
        if not Category.objects.filter(id=data['category'].id).exists():
            raise serializers.ValidationError("Category with this id does not exist.")
        return data


class Orderserilizer(serializers.ModelSerializer):
    # user=serializers.SlugRelatedField(queryset=Register.objects.all(),slug_field='user_order')
    # product=serializers.SlugRelatedField(queryset=Product.objects.all(),slug_field='product')
    # user = serializers.StringRelatedField(read_only=True)
    # product = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Order
        exclude = ['is_delete']
        # fields = '__all__'

class OrderDetailsserilizer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        # fields = '__all__'
        exclude = ['is_delete']

    
class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        exclude = ['is_delete']

              
    # def validate(self, data):
    #     if data == None:
    #         return Response({"error": True, "status_code": 400, "message": "Invalid data provided"})


class Rolepermissionserilizer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='rolename'
    )
    permission = serializers.SlugRelatedField(
        queryset=Permission.objects.all(),
        slug_field='permission_name'
    )

    class Meta:
        model = RolePermission
        fields = '__all__'



class RoleUserserilizer(serializers.ModelSerializer):
    class Meta:
        model = RoleUser
        # fields = '__all__'
        exclude = ['is_delete']
        