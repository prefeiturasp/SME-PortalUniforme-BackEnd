from django.urls import path, include
from rest_framework import routers

from .api.viewsets.proponentes_viewset import ProponentesViewSet
from .api.viewsets.tipos_documento_viewset import TiposDocumentoViewSet

router = routers.DefaultRouter()

router.register('proponentes', ProponentesViewSet)
router.register('tipos-documento', TiposDocumentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
