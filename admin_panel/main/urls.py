from django.contrib import admin
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


router = DefaultRouter()
router.register('rolePermission',views.RolePermissionviewset,basename='role_permission') # role details
router.register('category',views.Categoryserilizerviewset,basename='category')
router.register('product',views.Productserilizerviewset,basename='product')
# router.register('order',views.Orderserilizerviewset,basename='order')
router.register('order_details',views.OrderDetailsserilizerviewset,basename='order_details')
router.register('users',views.userviewset,basename='users')  
router.register('roles',views.Roleviewset,basename='roles')  #CRUD Role
router.register('permission',views.Permisssionviewset,basename='permission')  #CRUD Permissions
router.register('allorder',views.Allorder,basename='allorder')  #CRUD AllOrders
router.register('allorderdetails',views.AllordeerDetails,basename='allorderdetails')  #CRUD AllOrderDetails
router.register('UserRole',views.UserRoleviewset,basename='UserRole')  #CRUD AllOrderDetails

urlpatterns = [
    path('',include(router.urls)),
    path('register/',views.Registerviewset.as_view()),
    path('home',views.home),


    # Login 
    path("login/", views.Loginviewset.as_view()),
    path("otp/", views.Otpverification.as_view()),
    path("logout/", views.Logout.as_view()),
    path("forcelogout/", views.forceloogout.as_view()),
    path('active_users/', views.ActivateUser.as_view(), name='active_users'),
    path('all_users/', views.usersviewset.as_view(), name='users'),


    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
    path('order/', views.Orderserilizerviewset.as_view(), name='order'),

]
