from django.urls import include, path
from rest_framework import routers

# Importe aqui as rotas das demais aplicações
from sme_uniforme_apps.proponentes.urls import router as proponentes_router
from .viewsets.uniformes_viewset import UniformesViewSet
from .viewsets.version_viewset import ApiVersion

router = routers.DefaultRouter()

router.register('api-version', ApiVersion, basename='Version')
router.register('uniformes', UniformesViewSet)

# Adicione aqui as rotas das demais aplicações para que as urls sejam exibidas na API Root do DRF
router.registry.extend(proponentes_router.registry)

urlpatterns = [
    path('', include(router.urls))
]
