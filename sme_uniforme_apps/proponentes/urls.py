from django.urls import include, path
from rest_framework import routers

from .api.viewsets.anexos_viewset import AnexosViewset
from .api.viewsets.proponentes_viewset import ProponentesViewSet
from .api.viewsets.tipos_documento_viewset import TiposDocumentoViewSet

router = routers.DefaultRouter()

router.register('proponentes', ProponentesViewSet)
router.register('tipos-documento', TiposDocumentoViewSet)
router.register('anexos', AnexosViewset)

urlpatterns = [
    path('', include(router.urls)),
]
