from rest_framework import routers
from django.urls import include, path
from .viewsets.version_viewset import ApiVersion
from .viewsets.uniformes_viewset import UniformesViewSet
from .viewsets.meios_de_recebimento_viewset import MeiosDeRecebimentoViewSet

# Importe aqui as rotas das demais aplicações
from sme_uniforme_apps.proponentes.urls import router as proponentes_router

router = routers.DefaultRouter()

router.register('api-version', ApiVersion, basename='Version')
router.register('uniformes', UniformesViewSet)
router.register('meios-de-recebimento', MeiosDeRecebimentoViewSet)

# Adicione aqui as rotas das demais aplicações para que as urls sejam exibidas na API Root do DRF
router.registry.extend(proponentes_router.registry)

urlpatterns = [
    path('', include(router.urls))
]
