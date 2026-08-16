from django.contrib import admin
from .models import Project, Task, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
