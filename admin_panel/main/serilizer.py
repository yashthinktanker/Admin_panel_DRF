from rest_framework import serializers
from .models import *

class Registerserilizer(serializers.ModelSerializer):
  
    class Meta:
        model = Register
        exclude = ['created_at','updated_at']

class Roleseri(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class Permissionseri(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class Roleserilizer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Register.objects.all())
    class Meta:
        model = RoleUser
        fields = '__all__'

class Categoryserilizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class Productserilizer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):
        if Product.objects.filter(product_name=data['product_name']).exists():
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
        fields = '__all__'

class OrderDetailsserilizer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = '__all__'
        


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