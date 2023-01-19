"""
Views for Recipe API.
"""
from rest_framework import (
    viewsets,
    authentication,
    permissions,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

from core.models import Recipe

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for request."""
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe"""
        serializer.save(user=self.request.user)