from django.urls import path
from . import views
urlpatterns = [
    path(r'orders/settlement/$', views.OrderSettlementView.as_view()),
]