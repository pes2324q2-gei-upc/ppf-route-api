from django.urls import path
from api.views import (RouteListCreateView,
                       RouteRetrieveUpdateDestroyView,
                       RouteJoinView,
                       RouteLeaveView,
                       RouteCancelView)

urlpatterns = [
    path('routes/', RouteListCreateView.as_view(), name='route-list-create'),
    path('routes/<int:pk>/', RouteRetrieveUpdateDestroyView.as_view(), name='route-detail'),
    path('routes/<int:pk>/join/', RouteJoinView.as_view(), name='route-join'),
    path('routes/<int:pk>/leave/', RouteLeaveView.as_view(), name='route-leave'),
    path('routes/<int:pk>/cancel/', RouteCancelView.as_view(), name='route-cancel'),
]
