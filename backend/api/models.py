from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField('项目名称', max_length=100)
    description = models.TextField('项目描述', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='创建者'
    )

    members = models.ManyToManyField(
        User,
        related_name='projects',
        blank=True,
        verbose_name='成员'
    )

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Task(models.Model):

    class Status(models.TextChoices):
        TODO = 'TODO', '待办'
        IN_PROGRESS = 'IN_PROGRESS', '进行中'
        DONE = 'DONE', '已完成'

    class Priority(models.TextChoices):
        LOW = 'LOW', '低'
        MEDIUM = 'MEDIUM', '中'
        HIGH = 'HIGH', '高'

    title = models.CharField('任务标题', max_length=200)
    description = models.TextField('任务描述', blank=True, default='')
    status = models.CharField(
        '任务状态',
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        '优先级',
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    due_date = models.DateField('截止日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='所属项目'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='指派人'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='创建者'
    )

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属任务'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='作者'
    )

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} - {self.content[:20]}'
