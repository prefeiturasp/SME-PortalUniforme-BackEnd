from des import urls as des_url

from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework_swagger.views import get_swagger_view
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token,obtain_jwt_token

from sme_uniforme_apps.core.api.urls import urlpatterns as core_url
from sme_uniforme_apps.proponentes.urls import urlpatterns as proponentes_url

schema_view = get_swagger_view(title="Portal SME Uniformes")

urlpatterns = [
                  # Django Admin, use {% url 'admin:index' %}
                  path(settings.ADMIN_URL, admin.site.urls),
                  path("docs/", schema_view),
                  path("api-token-auth/", obtain_jwt_token),
                  path("refresh-token-auth/", refresh_jwt_token),
                  path("verify-token-auth/", verify_jwt_token),
                  path("django-des/", include(des_url)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += core_url
urlpatterns += proponentes_url

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    # urlpatterns += [
    #     path(
    #         "400/",
    #         default_views.bad_request,
    #         kwargs={"exception": Exception("Bad Request!")},
    #     ),
    #     path(
    #         "403/",
    #         default_views.permission_denied,
    #         kwargs={"exception": Exception("Permission Denied")},
    #     ),
    #     path(
    #         "404/",
    #         default_views.page_not_found,
    #         kwargs={"exception": Exception("Page not Found")},
    #     ),
    #     path("500/", default_views.server_error),
    # ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
