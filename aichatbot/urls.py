# from django.urls import path
# from .views import (
#     AIChatbotAPIView,
#     AIChatbotHealthAPIView,
#     ChatbotConfigAPIView,
#     ChatLeadCreateAPIView,
# )

# urlpatterns = [
#     path("health/", AIChatbotHealthAPIView.as_view(), name="ai-chatbot-health"),
#     path("config/", ChatbotConfigAPIView.as_view(), name="ai-chatbot-config"),
#     path("chat/", AIChatbotAPIView.as_view(), name="ai-chatbot-chat"),
#     path("lead/", ChatLeadCreateAPIView.as_view(), name="ai-chatbot-lead"),
# ]

from django.urls import path
from .views import (
    AIChatbotAPIView,
    AIChatbotHealthAPIView,
    ChatbotConfigAPIView,
    ChatLeadCreateAPIView,
    ChatbotWidgetJSAPIView,
)

urlpatterns = [
    path("health/", AIChatbotHealthAPIView.as_view(), name="ai-chatbot-health"),
    path("config/", ChatbotConfigAPIView.as_view(), name="ai-chatbot-config"),
    path("chat/", AIChatbotAPIView.as_view(), name="ai-chatbot-chat"),
    path("lead/", ChatLeadCreateAPIView.as_view(), name="ai-chatbot-lead"),
    path("widget.js", ChatbotWidgetJSAPIView.as_view(), name="ai-chatbot-widget-js"),
]