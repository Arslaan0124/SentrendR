from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import BasePermission, IsAdminUser,IsAuthenticated

from .serializers import UserSerializer,UserTierSerializer
from. models import CustomUser as User,UserTier


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
from .constants import ADMIN_USER

from core.models import Trend


def get_admin_user():
    user = User.objects.get(username= ADMIN_USER)
    return user



# Create your views here.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @permission_classes([IsAuthenticated])
    @action(detail=True, methods=['put'])
    def change_password(self,request, pk = None):


        user = User.objects.get(pk=pk)
        password = request.data['new_password']

        user.set_password(password)
        user.save()


        serializer = UserSerializer(user,many=False,context={'request': request})

        return Response(serializer.data)











class UserTierViewSet(viewsets.ModelViewSet):
    queryset = UserTier.objects.all()
    serializer_class = UserTierSerializer


    @action(detail=False, methods=['get','post'])
    def get_teir_info(self,request):

        trend_count = len(Trend.objects.filter(users = request.user))
        user_tier_info = UserTier.objects.get(customuser= request.user)

        user_tier_data={}
        user_tier_data['tier_name'] = user_tier_info.tier_name
        user_tier_data['max_keywords'] = user_tier_info.max_keywords
        user_tier_data['current_keywords'] = trend_count


        return Response(user_tier_data)


    
    def set_user_tier(self,request):
        pass