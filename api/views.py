from django.shortcuts import render
from rest_framework import viewsets, permissions
from api.serializers import RouteSerializer
from ppf.common.models import Route

# Create your views here.
class RouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows routes to be viewed or edited.
    """
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)
