from rest_framework import serializers
from .models import *

class Registerserilizer(serializers.ModelSerializer):
  
    class Meta:
        model = Register
        exclude = ['created_at','updated_at']

class Role(serializers.ModelSerializer):
    class Meta:
        model = Role
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
    class Meta:
        model = Order
        fields = '__all__'

class OrderDetailsserilizer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = '__all__'
        



