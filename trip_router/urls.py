from django.urls import path
from . import views

urlpatterns = [
    path('plan-route/', views.PlanRouteView.as_view(), name='plan-route'),
]