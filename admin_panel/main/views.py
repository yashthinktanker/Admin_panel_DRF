
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .models import *   
import random
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serilizer import Registerserilizer,Rolepermissionserilizer,Categoryserilizer,Productserilizer,Orderserilizer,OrderDetailsserilizer,RoleUserserilizer,Roleseri,Permissionseri  
from django.core.mail import send_mail,EmailMessage
from main.permissions import *
from rest_framework import  viewsets
from main.permissions  import Dynamicpermission,Assignedpermissionset
from main.mypagination import mypaginatior
from django_filters.rest_framework import  DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response

def Custome_Response(error,message,status_code=200, data={}):
    return Response({
        "error": error,
        "status_code": status_code,
        "message": message,
        "data": data
    }, status=status_code)


# Create your views here.
def home(request):
    return render(request,'home.html')

def random_password(length):
    password=""
    for i in range(length):
        password+=random.choice(
            [
                str(random.randint(0,9)),
                chr(random.choice([random.randint(65,90),random.randint(97,123)]))
            ]
        )
    return password


class Registerviewset(APIView):
    def post(self, request):
        data = request.data.copy()

        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return Custome_Response(True, "Username and email are required.", status_code=400)

        if Register.objects.filter(email=email).exists():
            return Custome_Response(True, "This email address is already registered.", status_code=400)

        password = random_password(6)
        print('password: ', password)

        data['password'] = make_password(password)
        data['gender'] = 'male'

        serializer = Registerserilizer(data=data)

        if serializer.is_valid():
            user = serializer.save()

            role = Role.objects.get(rolename="User")
            RoleUser.objects.create(user=user, role=role)

            EmailMessage(
                "Your Password",
                f"Your password is {password}",
                None,
                [email],
            ).send()

            return Custome_Response(False, "User registered successfully.", status_code=201)

        return Custome_Response(True, "Invalid data provided.", status_code=400)

class RolePermissionviewset(viewsets.ModelViewSet):
    serializer_class = Rolepermissionserilizer
    queryset = RolePermission.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Assignedpermissionset]




class Categoryserilizerviewset(viewsets.ModelViewSet):
    serializer_class = Categoryserilizer
    queryset = Category.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Dynamicpermission]
    def destroy(self, request,pk):
        print(pk)
        x=Category.objects.filter(id=pk).first()
        if x:
            x.delete()
            return Custome_Response(False, "Category deleted successfully.", status_code=200)
        return Custome_Response(True, "Category not found.", status_code=400)
    
class Productserilizerviewset(viewsets.ModelViewSet):   
    serializer_class = Productserilizer
    queryset = Product.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Dynamicpermission]

    # pagination_class=mypaginatior
    filter_backends=[DjangoFilterBackend,SearchFilter]
    SearchFilter=['category']

    def destroy(self, request,pk):
        print(pk)
        x=Product.objects.filter(id=pk).first()
        if x:
            x.delete()
            return Custome_Response(False, "Product deleted successfully.", status_code=200)
        return Custome_Response(True, "Product not found.", status_code=400)

class Orderserilizerviewset(APIView):

    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Orderpermission]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user.id)
        print('orders: ', orders)

        serializer = Orderserilizer(orders, many=True)

        return Custome_Response(False, "Orders retrieved successfully.", status_code=200, data=serializer.data)
    
    def post(self,request):
        print('request.data: ', request.user)
        u=Register.objects.get(username=request.user)
        print('u: ', u.id)
        data=request.data.copy()
        data['user']=u.id
        seri=Orderserilizer(data=data)
        if seri.is_valid():
            x=seri.save()
            OrderDetails.objects.create(order=x)
            return Custome_Response(False, "Order created successfully.", status_code=201, data=seri.data)  
        return Custome_Response(True, "Unable to create order. Please provide valid data.", status_code=400)


class OrderDetailsserilizerviewset(viewsets.ModelViewSet):
    serializer_class = OrderDetailsserilizer
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Dynamicpermission]
    
    def get_queryset(self):
        user = self.request.user

        try:
            u = Register.objects.get(id=user.id)
            orders = Order.objects.filter(user=u)

            if not orders.exists():
                return OrderDetails.objects.none()

            return OrderDetails.objects.filter(order__in=orders)

        except Register.DoesNotExist:
            return OrderDetails.objects.none()

def otp_genrate(length):
    otp=""
    for i in range(length):
        otp+=str(random.randint(0, 9))
    return otp



class Loginviewset(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        errors = {}

        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'

        if errors:
            return  Custome_Response(True, errors, status_code=400)

        try:
            user = Register.objects.get(email=email)
        except Register.DoesNotExist:
            return Custome_Response(True, "Email address is not registered.", status_code=404)

        if not check_password(password, user.password):
            return Custome_Response(True, "Incorrect password.", status_code=400)

        # Generate OTP
        otp = otp_genrate(6)
        print('otp: ', otp)
        user.otp = otp
        user.save()

        EmailMessage(
            "OTP Verification",
            f"Your login OTP is {otp}",
            None,
            [email],
        ).send()
        request.session['user_id'] = user.id  # Store user ID in session
        return Custome_Response(False, "OTP sent successfully.", status_code=200, data={"user_id": user.id})   # ✅ FIX


    
class Otpverification(APIView):
    def post(self, request):
        user_id = request.session.get('user_id')  # Retrieve user ID from session
        print('user_id: ', user_id)
        otp = request.data.get('otp')

        if not otp:
            return Custome_Response(True, "OTP is required.", status_code=400)

        try:
            user = Register.objects.get(id=user_id)
        except Register.DoesNotExist:
            return Custome_Response(True, "User not found.", status_code=404)

        if str(user.otp) != str(otp):
            return Custome_Response(True, "Invalid OTP.", status_code=400)

        # Activate user
        user.is_verify = True
        user.is_active = True
        user.otp = ''
        user.save()

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        return Custome_Response(False, "OTP verified successfully.", status_code=200, data={
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
        request.session.pop('user_id', None)  # Clear user ID from session after verification
    
class Logout(APIView):
    def get(self,request):
        try:
            user_id = request.user.id
            user = Register.objects.get(id=user_id)
    
            if user :
                user.is_active = False
                user.is_staff = False
                user.save()
                return Custome_Response(False, "Logged out successfully.", status_code=201)
            else:
                return Custome_Response(True, "OTP verification is required before logout.", status_code=400)
        except:
            return Custome_Response(True, "You are already logged out. Please log in again.", status_code=400)
        

class forceloogout(APIView):
    def get(self,request):
        request.user.is_active = False
        request.user.is_staff = False
        request.user.save()
        return Custome_Response(False, "Logged out successfully.", status_code=200)
    
class ChangePassword(APIView):
    def post(self,request):
        data=request.data
        old_password=data.get('old_password')
        new_password=data.get('new_password')
        user_id = request.user.id
        if not old_password:
            return Custome_Response(True, "Old password is required.", status_code=400)    
        if not new_password:
            return Custome_Response(True, "New password is required.", status_code=400)
        
        if old_password == new_password:
            return Custome_Response(True, "Old password and new password cannot be the same.", status_code=400)

        if not user_id:
            return Custome_Response(True, "Session expired. Please log in again.", status_code=400)

        try:
            user = Register.objects.get(id=user_id)
            if not check_password(old_password, user.password):
                return Custome_Response(True, "Old password is incorrect.", status_code=400)
            user.password = make_password(new_password)
            user.save()
            return Custome_Response(False, "Password changed successfully.", status_code=200)
        except Register.DoesNotExist:
            return Custome_Response(True, "User not found.", status_code=400)
        


class usersviewset(APIView):
    def get(self,request):
        if not request.user:
            return Custome_Response(True, "Please log in to continue.", status_code=400)
        user = request.user.id
        try:
            x = RoleUser.objects.get(user_id=user)
            print('x: ', x.role.rolename)
        except RoleUser.DoesNotExist:
            return Custome_Response(True, "User not found.", status_code=400)

        if x.role.rolename != 'Admin' and x.role.rolename != 'Manager':
            return Custome_Response(True, "You do not have permission to access this resource.", status_code=400)
        users_count = Register.objects.count()
        users = Register.objects.all()
        return Response({
            "error": False,
            "status_code": 200,
            "message": "Users retrieved successfully.",
            "total_users": users_count,
            "data":  Registerserilizer(users, many=True).data
        }, status=200)
    
class ActivateUser(APIView):
    def get(self,request):  
        if not request.user:
            return Custome_Response(True, "Please log in to continue.", status_code=400)
        user = request.user.id
        
        try:
            x = RoleUser.objects.get(user_id=user)
            print('x: ', x.role.rolename)
        except RoleUser.DoesNotExist:
            return Custome_Response(True, "User not found.", status_code=400)

        if x.role.rolename != 'Admin' and x.role.rolename != 'Manager':
            return Custome_Response(True, "You do not have permission to access this resource.", status_code=400)
        users_count = Register.objects.filter(is_active=True).count()
        users = Register.objects.filter(is_active=True)
        return Response({
            "error": False,
            "status_code": 200,
            "message": "Active users retrieved successfully.",
            "total_users": users_count,
            "data":  Registerserilizer(users, many=True).data
        }, status=200)

class userviewset(viewsets.ModelViewSet):
    serializer_class = Registerserilizer
    queryset = Register.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,IsAdminOrManager]
    pagination_class = mypaginatior 

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email']

    def destroy(self, request,pk):
        print(pk)
        x=Register.objects.filter(id=pk).first()
        if x:
            x.delete()
            return Custome_Response(False, "User deleted successfully.", status_code=200)
        return Custome_Response(True, "User not found.", status_code=400)

class Roleviewset(viewsets.ModelViewSet):
    serializer_class =  Roleseri
    queryset = Role.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]

    def destroy(self, request,pk):
        print(pk)
        x=Role.objects.filter(id=pk,is_delete=False).first()
        if x:
            x.delete()
            return Custome_Response(False, "Role deleted successfully.", status_code=200)
        return Custome_Response(True, "Record not found.", status_code=400)



class Permisssionviewset(viewsets.ModelViewSet):
    serializer_class = Permissionseri
    queryset = Permission.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]


    def destroy(self, request,pk):
        print(pk)
        x=Permission.objects.filter(id=pk).first()
        if x:
            x.delete()
            return Custome_Response(False, "Permission deleted successfully.", status_code=200)
        return Custome_Response(True, "Record not found.", status_code=400)
    


class Allorder(viewsets.ModelViewSet):
    serializer_class=Orderserilizer
    queryset = Order.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]
    http_method_names=['get']
    
class AllordeerDetails(viewsets.ModelViewSet):
    serializer_class=OrderDetailsserilizer
    queryset = OrderDetails.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]
    http_method_names=['get']


class UserRoleviewset(viewsets.ModelViewSet):
    serializer_class = RoleUserserilizer
    queryset = RoleUser.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminrole]


