from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny


class AdminOrReadOnly(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]
