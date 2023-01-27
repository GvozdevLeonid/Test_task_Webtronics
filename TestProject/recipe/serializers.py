"""
Serializers for recipe API view.
"""
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    ingredients = IngredientSerializer(many=True, required=False)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['ingredients', 'description', 'image']

    def _add_tags(self, tags, recipe):
        user = self.context['request'].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(
                    user=user,
                    **tag,
            )
            recipe.tags.add(tag_object)

    def _add_ingredients(self, ingredients, recipe):
        user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_object, created = Ingredient.objects.get_or_create(
                    user=user,
                    **ingredient,
            )
            recipe.ingredients.add(ingredient_object)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)

        self._add_tags(tags, recipe)
        self._add_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._add_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._add_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for upload recipe image."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}