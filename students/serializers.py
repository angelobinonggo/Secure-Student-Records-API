"""
serializers.py — StudentRecord and User serializers
"""
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import StudentRecord


class UserSerializer(serializers.ModelSerializer):
    """Read-only user info (safe fields only)."""
    groups = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registers a new user and optionally assigns them to a group.
    Accepted role values: 'Admin', 'Faculty', 'Student'
    """
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=['Admin', 'Faculty', 'Student'],
        write_only=True,
        default='Student'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', 'Student')
        user = User.objects.create_user(**validated_data)
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        return user


class StudentRecordSerializer(serializers.ModelSerializer):
    """Full serializer for admin/faculty access."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = StudentRecord
        fields = [
            'id', 'owner', 'owner_username',
            'full_name', 'course', 'year_level', 'gpa',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'owner_username']


class StudentRecordReadSerializer(serializers.ModelSerializer):
    """Restricted serializer for student self-view (hides owner FK)."""
    class Meta:
        model = StudentRecord
        fields = ['id', 'full_name', 'course', 'year_level', 'gpa', 'updated_at']
        read_only_fields = fields
