from django.urls import path, include
from rest_framework import routers

from .api.viewsets.proponentes_viewset import ProponentesViewSet

router = routers.DefaultRouter()

router.register('proponentes', ProponentesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
