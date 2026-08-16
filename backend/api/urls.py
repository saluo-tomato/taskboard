from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserRegisterView,
    UserProfileView,
    UserListView,
    ProjectViewSet,
    TaskViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterView.as_view(), name='user_register'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),

    path('users/', UserListView.as_view(), name='user-list'),

    path('projects/<int:project_pk>/tasks/<int:task_pk>/comments/',
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='project-task-comments'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/comments/<int:pk>/',
         CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='project-task-comment-detail'),

    path('tasks/<int:task_pk>/comments/',
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='task-comments'),
    path('tasks/<int:task_pk>/comments/<int:pk>/',
         CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='task-comment-detail'),

    path('', include(router.urls)),
]
