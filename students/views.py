"""
views.py — API views for student records (Part D of Lab Activity 1)
"""
from django.contrib.auth.models import User, Group
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentRecord
from .serializers import (
    RegisterSerializer,
    StudentRecordReadSerializer,
    StudentRecordSerializer,
    UserSerializer,
)
from .permissions import IsAdminUser, IsAdminOrFaculty, IsOwnerOrAdminOrFaculty


# ─── User Registration ────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/register/
    Public endpoint — create a new user and assign them a role group.
    Body: { username, email, password, first_name, last_name, role }
    role choices: Admin | Faculty | Student  (default: Student)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": f"User '{user.username}' registered successfully.",
                    "role": request.data.get('role', 'Student'),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Current User Profile ─────────────────────────────────────────────────────

class MeView(APIView):
    """
    GET /api/me/
    Returns the authenticated user's profile and assigned groups/roles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ─── Student Record ViewSet ───────────────────────────────────────────────────

class StudentRecordViewSet(viewsets.ModelViewSet):
    """
    /api/student-records/
    CRUD endpoint protected by Role-Based Access Control (RBAC).

    Permission matrix
    ─────────────────────────────────────────────────────
    Action              | Admin | Faculty | Student
    ─────────────────────────────────────────────────────
    list (GET all)      |  ✓    |   ✓     | own only
    retrieve (GET one)  |  ✓    |   ✓     | own only
    create (POST)       |  ✓    |   ✗     |    ✗
    update (PUT/PATCH)  |  ✓    |   ✓     |    ✗
    destroy (DELETE)    |  ✓    |   ✗     |    ✗
    ─────────────────────────────────────────────────────
    """
    serializer_class = StudentRecordSerializer

    # ── Per-action permission assignment ──────────────────────────────────────
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrFaculty]
        else:
            # list, retrieve — authenticated users, object-level enforced below
            permission_classes = [IsOwnerOrAdminOrFaculty]
        return [perm() for perm in permission_classes]

    # ── Queryset: students see only their own records ─────────────────────────
    def get_queryset(self):
        user = self.request.user
        is_admin_or_faculty = (
            user.is_superuser
            or user.groups.filter(name__in=['Admin', 'Faculty']).exists()
        )
        if is_admin_or_faculty:
            return StudentRecord.objects.select_related('owner').all()
        # Students: own records only
        return StudentRecord.objects.filter(owner=user)

    # ── Serializer: students get restricted read-only view ────────────────────
    def get_serializer_class(self):
        user = self.request.user
        is_admin_or_faculty = (
            user.is_superuser
            or user.groups.filter(name__in=['Admin', 'Faculty']).exists()
        )
        if not is_admin_or_faculty and self.action in ['list', 'retrieve']:
            return StudentRecordReadSerializer
        return StudentRecordSerializer

    # ── Auto-set owner on creation ────────────────────────────────────────────
    def perform_create(self, serializer):
        # If admin doesn't specify an owner, default to themselves
        if 'owner' not in self.request.data:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    # ── Extra action: list records belonging to a specific user ───────────────
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[0-9]+)',
            permission_classes=[IsAdminOrFaculty])
    def by_user(self, request, user_id=None):
        """GET /api/student-records/by-user/<user_id>/ — Admin/Faculty only."""
        records = StudentRecord.objects.filter(owner_id=user_id)
        if not records.exists():
            return Response(
                {"detail": "No records found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StudentRecordSerializer(records, many=True)
        return Response(serializer.data)
