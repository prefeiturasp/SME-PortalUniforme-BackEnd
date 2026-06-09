from django.urls import path

from .views import TriadeCallbackWebhookView

urlpatterns = [
    path(
        "triade/callback/", TriadeCallbackWebhookView.as_view(), name="triade-callback"
    ),
]
