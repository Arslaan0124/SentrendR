from django.urls import path,include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

router = DefaultRouter()
router.register(r'crawlers',views.CrawlerViewSet)
router.register(r'streams',views.StreamDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]