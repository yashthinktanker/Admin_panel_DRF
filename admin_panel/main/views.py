from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.
def home(request):
    return render(request,'home.html')

from rest_framework.views import APIView
from .models import *   
from main.serilizer import *
import random,requests
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.core.mail import send_mail,EmailMessage

from main.permissions import *

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


from rest_framework.response import Response
class Registerviewset(APIView):
    def post(self, request):
        errors = {}
        data = request.data.copy()

        name = data.get('username')
        email = data.get('email')

        if not name:
            errors['name'] = 'UserName Is Required'

        if not email:
            errors['email'] = 'Email Is Required'

        if email:
            if Register.objects.filter(email=email).exists():
                errors['email'] = 'Email already exists'

        if errors:
            return Response({"error": True, "status_code": 400, "message": str(errors)})


        gender = 'male'

        # Random password
        password = random_password(6)
        print('password: ', password)

        data['password'] = make_password(password)
        data['gender'] = gender

        serializer = Registerserilizer(data=data)

        if serializer.is_valid():
            try:
                x= serializer.save()

                #  Create role after user created
                role_obj = Role.objects.get(rolename="User")
                RoleUser.objects.create(user=x, role=role_obj)

                # Send email
                EmailMessage(
                    "Your Email Password",
                    f"Your login password is {password}",
                    None,
                    [email],
                ).send()

                return Response({"error": False, "status_code": 201, "message":f"Register Successfully & Password sent to {email}"})

            except Exception as e:
                return Response({"error": False, "status_code": 400, "message":"demo"})

        return Response({"error": False, "status_code": 400, "message":str(serializer.errors)})
    

from rest_framework import  viewsets

from main.permissions  import Dynamicpermission,Assignedpermissionset
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


from main.mypagination import mypaginatior
from django_filters.rest_framework import  DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter


class Productserilizerviewset(viewsets.ModelViewSet):   
    serializer_class = Productserilizer
    queryset = Product.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Dynamicpermission]

    # pagination_class=mypaginatior
    filter_backends=[DjangoFilterBackend,SearchFilter]
    SearchFilter=['category']




class Orderserilizerviewset(APIView):

    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,Orderpermission]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        print('orders: ', orders)

        serializer = Orderserilizer(orders, many=True)

        return Response({
            "error": False,
            "status_code": 200,
            "message": "Display Data",
            "Data": serializer.data
        })
    
    def post(self,request):
        data=request.data.copy()
        data['user']=request.session.get('user')
        seri=Orderserilizer(data=data)
        if seri.is_valid():
            x=seri.save()
            OrderDetails.objects.create(order=x)
            return Response({
                "error": False,
                "status_code": 201,
                "message": "Display Data",
                "Data": seri.data
            })  
        return Response({
            "error": True,
            "status_code": 400,
            "message": "Not Data Add",
        })


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

from django.contrib.auth.hashers import check_password

class Loginviewset(APIView):
    def post(self,request):
        # user=request.session.get('user')
        
        # if user:
        #     try:
        #         Register.objects.get(id=user)
        #         return Response({'Message':'Already Login'})
        #     except Register.DoesNotExist:
        #         pass
        
        errors={}
        data = request.data.copy()

        email=data.get('email')


        if not email :
            errors['email']='Email Is Required'
        else:
            try:
                user = Register.objects.get(email=email)
                print('user: ', user.password)
            except Register.DoesNotExist:
                errors['email']=  "User not found"

        password=data.get('password')
        print('password: ==', password)
        if not password:
            errors['password']='Password Is Required'


        if not check_password(password, user.password):
            errors['password']='Password Not Currect'
        
        if errors:
            return Response({"error": True, "status_code": 400, "message":errors})

        
        try:
            o=otp_genrate(6)
            print('otp: ', o)
            EmailMessage(
                    "OTP verifications",
                    f"Your login Otp is {o}",
                    None,
                    [email],
            ).send()
            request.session['user'] = user.id
            request.session['otp']=o
        except Exception as e:
            return Response({"error": True, "status_code": 400, "message":"Otp not send"})
        
        return Response({"error": False, "status_code": 201, "message":'Login Sucessful & OTP send On Mail'})
    

from rest_framework_simplejwt.tokens import RefreshToken
class Otpverification(APIView):
    def post(self,request):
        data=request.data
        otp=data.get('otp')
        print( otp,request.session.get('otp'))

        if not otp:
            return Response({"error": "Enter OTP"})
        if str(otp) != str(request.session.get('otp')):
            return Response({"error": True, "status_code": 400, "message":"Invaide OTP"})
        
        user_id = request.session.get('user')

        if not user_id:
            return Response({"error": True, "status_code": 400, "message":"Session expired. Please login again"})

        try:
            user = Register.objects.get(id=user_id)
            user.is_verify = True
            user.is_staff = True
            user.is_active = True
            user.save()
    

        except Register.DoesNotExist:
            return Response({"error": True, "status_code": 400, "message":"User not found"})

        refresh = RefreshToken.for_user(user)
        request.session.pop('otp', None)
        


        return Response({
            "error": False, "status_code": 201,
            'message': 'OTP Confirmed',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
    
class Logout(APIView):
    def get(self,request):
        try:
            user_id = request.session['user']
            user = Register.objects.get(id=user_id)
    
            if user :
                user.is_active = False
                user.is_staff = False
                user.save()
                
                request.session.pop('user')
                return Response({"error": False, "status_code": 201,'message': 'Logout'})
            else:
                return Response({"error": True, "status_code": 400,'message':'OTP Verification not pls Otp verified'})
        except:
            return Response({"error": True, "status_code": 400,'message':'Alredy logout pls login'})
        

class forceloogout(APIView):
    def get(self,request):
        request.session.pop('user')
        return Response({"error": False, "status_code": 200,'message': 'Logout'})
    

# change password
class ChangePassword(APIView):
    def post(self,request):
        data=request.data
        old_password=data.get('old_password')
        new_password=data.get('new_password')
        user_id = request.session.get('user')
        if not old_password:
            return Response({"error": True, "status_code": 400,"message": "Enter Old Password"})    
        if not new_password:
            return Response({"error": True, "status_code": 400,"message": "Enter New Password"})
        
        if old_password == new_password:
            return Response({"error": True, "status_code": 400,"message": "Old Password and New Password cannot be the same"})

        if not user_id:
            return Response({"error": True, "status_code": 400,"message": "Session expired. Please login again"})

        try:
            user = Register.objects.get(id=user_id)
            if not check_password(old_password, user.password):
                return Response({"error": True, "status_code": 400,"message": "Old password is incorrect"})
            user.password = make_password(new_password)
            user.save()
            return Response({"error": False, "status_code": 200,"message": "Password changed successfully"})
        except Register.DoesNotExist:
            return Response({"error": True, "status_code": 400,"error": "User not found"})
        


class usersviewset(APIView):
    def get(self,request):
        if not request.session.get('user'):
            return Response({"error": True, "status_code": 400, "message": "Pls Login"})
        user = request.session.get('user')
        try:
            x = RoleUser.objects.get(user_id=user)
            print('x: ', x.role.rolename)
        except RoleUser.DoesNotExist:
            return Response({"error": True, "status_code": 400, "message": "User not found"})

        if x.role.rolename != 'Admin' and x.role.rolename != 'Manager':
            return Response({"error": True, "status_code": 400, "message": "You don't have permission to access this resource"})
        users_count = Register.objects.count()
        users = Register.objects.all()
        return Response({"error": False, "status_code": 200, "message": "Success", "data": {'Total user:': users_count, 'users': Registerserilizer(users, many=True).data}}) 
    

class ActivateUser(APIView):
    def get(self,request):
        if not request.session.get('user'):
            return Response({"error": True, "status_code": 400, "message": "Pls Login"})
        user = request.session.get('user')
        try:
            x = RoleUser.objects.get(user_id=user)
            print('x: ', x.role.rolename)
        except RoleUser.DoesNotExist:
            return Response({"error": True, "status_code": 400, "message": "User not found"})

        if x.role.rolename != 'Admin' and x.role.rolename != 'Manager':
            return Response({"error": True, "status_code": 400, "message": "You don't have permission to access this resource"})
        users_count = Register.objects.filter(is_active=True).count()
        users = Register.objects.filter(is_active=True)
        return Response({"error": False, "status_code": 200, "message": "Success", "data": {'Total Active User:': users_count, 'users': Registerserilizer(users, many=True).data}})




class userviewset(viewsets.ModelViewSet):
    serializer_class = Registerserilizer
    queryset = Register.objects.all()
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated,IsAdminrole]
    pagination_class = mypaginatior 

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email']

class Roleviewset(viewsets.ModelViewSet):
    serializer_class =  Roleseri
    queryset = Role.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]

class Permisssionviewset(viewsets.ModelViewSet):
    serializer_class = Permissionseri
    queryset = Permission.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]


class Allorder(viewsets.ModelViewSet):
    serializer_class=Orderserilizer
    queryset = Order.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]

class AllordeerDetails(viewsets.ModelViewSet):
    serializer_class=OrderDetailsserilizer
    queryset = OrderDetails.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminOrManager]


class UserRoleviewset(viewsets.ModelViewSet):
    serializer_class = RoleUserserilizer
    queryset = Role.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminrole]