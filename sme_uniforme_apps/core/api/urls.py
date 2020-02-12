from django.urls import include, path

from .viewsets.parametros_viewset import ParametrosViewSet
from .viewsets.instrucao_normativa_viewset import InstrucaoNormativaViewSet
from rest_framework import routers

# Importe aqui as rotas das demais aplicações
from sme_uniforme_apps.proponentes.urls import router as proponentes_router
from .viewsets.limites_categorias_viewset import LimitesCategoriasViewSet
from .viewsets.uniformes_viewset import UniformesViewSet
from .viewsets.version_viewset import ApiVersion

router = routers.DefaultRouter()

router.register('api-version', ApiVersion, basename='Version')
router.register('uniformes', UniformesViewSet)
router.register('edital', ParametrosViewSet, basename='Edital')
router.register('instrucao-normativa', InstrucaoNormativaViewSet, basename='InstrucaoNormativa')
router.register('limites-categorias', LimitesCategoriasViewSet)

# Adicione aqui as rotas das demais aplicações para que as urls sejam exibidas na API Root do DRF
router.registry.extend(proponentes_router.registry)

urlpatterns = [
    path('', include(router.urls))
]
