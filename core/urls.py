from django.urls import path,include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

router = DefaultRouter()
router.register(r'trends', views.TrendViewSet)
router.register(r'tweets',views.TweetViewSet)
router.register(r'topics',views.TopicViewSet)
router.register(r'locations',views.LocationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('foo/',views.foo),
]