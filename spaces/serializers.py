from rest_framework import serializers
from .models import Document, Space, Revision


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ('id', 'name', 'path')


class RevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revision
        fields = (
            'id',
            'content',
            'created_on'
        )


class DocumentSerializer(serializers.ModelSerializer):
    space = serializers.SlugRelatedField(
        read_only=True,
        slug_field='path'
    )
    parent = serializers.SlugRelatedField(
        read_only=True,
        slug_field='full_path_property'
    )
    latest = RevisionSerializer(read_only=True)
    revision_set = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True)
    children = serializers.SlugRelatedField(
        many=True,
        slug_field='path',
        read_only=True)

    class Meta:
        model = Document
        fields = (
            'id',
            'title',
            'path',
            'space',
            'parent',
            'latest',
            'revision_set',
            'children'
        )
