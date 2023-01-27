"""
Views for Recipe API.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    authentication,
    permissions,
    mixins,
    status,
    response,
)
from rest_framework.decorators import action

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer,
)

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

@extend_schema_view(
        list=extend_schema(
                parameters=[
                    OpenApiParameter(
                            'tags',
                            OpenApiTypes.STR,
                            description='Comma separated list of tags IDs to filter.'
                    ),
                    OpenApiParameter(
                            'ingredients',
                            OpenApiTypes.STR,
                            description='Comma separated list of ingredients IDs to filter.'
                    )
                ]
        )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _parameters_to_list(self, parametes):
        """Convert list of string to int."""
        return [int(param) for param in parametes.split(",")]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset
        if tags:
            queryset = queryset.filter(tags__id__in=self._parameters_to_list(tags))

        if ingredients:
            queryset = queryset.filter(ingredients__id__in=self._parameters_to_list(ingredients))

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return serializer class for request."""
        if self.action == 'list':
            return RecipeSerializer

        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploading an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
        list=extend_schema(
                parameters=[
                    OpenApiParameter(
                            'assigned_only',
                            OpenApiTypes.INT,
                            enum=[0, 1],
                            description='Filter by items assigned to recipes.'
                    )
                ]
        )
)
class BaseRecipeAttrViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset by user."""
        assigned_only = bool(
                int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by('name').distinct()

    def perform_create(self, serializer):
        """Create a new object."""
        serializer.save(user=self.request.user)



class TagViewSet(BaseRecipeAttrViewSet):
    """View for manage Tags APIs."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

class IngredientViewSet(BaseRecipeAttrViewSet):
    """View for manage Tags APIs."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

