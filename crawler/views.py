from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated , IsAdminUser

from .models import Crawler,StreamData
from .serializers import CrawlerSerializer,StreamDataSerializer
# Create your views here.


class CrawlerViewSet(viewsets.ModelViewSet):
    queryset = Crawler.objects.all()
    serializer_class = CrawlerSerializer
    permission_classes = [IsAuthenticated]


class StreamDataViewSet(viewsets.ModelViewSet):
    queryset = StreamData.objects.all()
    serializer_class = StreamDataSerializer
    permission_classes = [IsAuthenticated]