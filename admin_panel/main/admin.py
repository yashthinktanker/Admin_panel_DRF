from django.contrib import admin
from main.models import *
# Register your models here.

admin.site.register(Register)
admin.site.register(RoleUser)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetails)

