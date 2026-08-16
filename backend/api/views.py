from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models

from .models import Project, Task, Comment
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    TaskListSerializer,
    TaskDetailSerializer,
    CommentSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'creator'):
            return obj.creator == request.user
        if hasattr(obj, 'author'):
            return obj.author == request.user
        return False


class IsProjectMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            project = obj
        elif hasattr(obj, 'project'):
            project = obj.project
        else:
            return False

        return (
            project.owner == request.user or
            project.members.filter(id=request.user.id).exists()
        )


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': '注册成功',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['username', 'email']


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct().select_related('owner').prefetch_related('members')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        project.members.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """添加项目成员"""
        project = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': '请提供user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            project.members.add(user)
            return Response({'message': f'已添加成员 {user.username}'})
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': '请提供user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if int(user_id) == project.owner.id:
            return Response(
                {'error': '不能移除项目创建者'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            project.members.remove(user)
            return Response({'message': f'已移除成员 {user.username}'})
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        project = self.get_object()
        tasks = project.tasks.all()

        total = tasks.count()
        todo = tasks.filter(status=Task.Status.TODO).count()
        in_progress = tasks.filter(status=Task.Status.IN_PROGRESS).count()
        done = tasks.filter(status=Task.Status.DONE).count()

        return Response({
            'total': total,
            'todo': todo,
            'in_progress': in_progress,
            'done': done,
            'completion_rate': round(done / total * 100, 1) if total > 0 else 0
        })


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members=user)
        ).distinct().select_related(
            'project', 'assignee', 'creator'
        ).prefetch_related('comments')

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')

        if new_status not in [s[0] for s in Task.Status.choices]:
            return Response(
                {'error': '无效的状态值'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()
        return Response(TaskDetailSerializer(task).data)

    @action(detail=True, methods=['patch'])
    def update_priority(self, request, pk=None):
        task = self.get_object()
        new_priority = request.data.get('priority')

        if new_priority not in [p[0] for p in Task.Priority.choices]:
            return Response(
                {'error': '无效的优先级值'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.priority = new_priority
        task.save()
        return Response(TaskDetailSerializer(task).data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return Comment.objects.filter(task_id=task_id).select_related('author')
        return Comment.objects.none()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)


