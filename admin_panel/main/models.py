from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
ROLE_CHOICES = [
        ("Manager", "Manager"),
        ("User", "User"),
        ("Viewer", "Viewer"),
    ]


class Nonedeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)
    
class SoftDelete(models.Model):
    is_delete = models.BooleanField(default=False)

    everithing = models.Manager()
    objects = Nonedeleted()

    def delete(self):
        self.is_delete = True
        self.save()

    def soft_delete(self):
        self.is_delete = True
    
    def restore(self):
        self.is_delete = False

    class Meta:
        abstract = True

class Role(SoftDelete):
    rolename = models.CharField(max_length=30)

    def __str__(self):
        return self.rolename


class Permission(SoftDelete):
    permission_name = models.CharField(max_length=50)

    def __str__(self):
        return self.permission_name


class RolePermission(SoftDelete):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE,related_name='permission_roles')

    def __str__(self):
        return f"{self.role.rolename} - {self.permission.permission_name}"
    
class Register(AbstractUser):
    # username = models.CharField(max_length=150, unique=True)
    # email = models.EmailField(unique=True)
    gender = models.CharField(max_length=7,default='male')
    # password = models.CharField(max_length=100,default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
class RoleUser(SoftDelete):
    user = models.OneToOneField(Register, on_delete=models.CASCADE, related_name='role')
    role = models.ForeignKey(Role, on_delete=models.CASCADE,default='User')

    def __str__(self):
        return f"{self.user.username} - {self.role.rolename}"

class Category(SoftDelete):
    category_name = models.CharField(max_length=16,unique=True)

    def __str__(self):
        return self.category_name

class Product(SoftDelete):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='category')
    product_name = models.CharField(max_length=50,null=False)

    def __str__(self):
        return f'{self.product_name}'
    

class Order(SoftDelete):
    user = models.ForeignKey(Register,on_delete=models.CASCADE,related_name='user_order') 
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product')
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

STATUS_CHOICES = [
        ("pending", "pending"),
        ("process", "process"),
        ("Completed", "Completed"),
    ]

class OrderDetails(SoftDelete):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order') 
    status = models.CharField(max_length=15,choices=STATUS_CHOICES,default='pending')

    def __str__(self):
        return self.status
    

