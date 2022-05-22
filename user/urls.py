from django.urls import path,include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns




router = DefaultRouter()


router.register(r'users', views.UserViewSet)
router.register(r'user_tiers', views.UserTierViewSet)











from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    #TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('auth/', include('rest_auth.urls')),    
    #path('auth/register/', include('rest_auth.registration.urls'))
]