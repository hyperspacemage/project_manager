# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Attachment(models.Model):
    task = models.ForeignKey('Task', models.DB_CASCADE)
    user = models.ForeignKey('User', models.DB_CASCADE)
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment'


class Comment(models.Model):
    task = models.ForeignKey('Task', models.DB_CASCADE)
    user = models.ForeignKey('User', models.DB_CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'


class Invitation(models.Model):
    project = models.ForeignKey('Project', models.DB_CASCADE)
    inviter = models.ForeignKey('User', models.DB_CASCADE)
    token = models.CharField(unique=True, max_length=100)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invitation'


class Priority(models.Model):
    level = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'priority'


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project'


class ProjectMember(models.Model):
    user = models.ForeignKey('User', models.DB_CASCADE)
    project = models.ForeignKey(Project, models.DB_CASCADE)
    role = models.ForeignKey('Role', models.DB_CASCADE)
    joined_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_member'
        unique_together = (('user', 'project'),)


class Role(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role'


class Task(models.Model):
    project = models.ForeignKey(Project, models.DB_CASCADE)
    priority = models.ForeignKey(Priority, models.DB_CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DB_CASCADE, db_column='created_by')
    assigned_to = models.ForeignKey('User', models.DB_SET_NULL, db_column='assigned_to', related_name='task_assigned_to_set', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task'


class User(models.Model):
    username = models.CharField(unique=True, max_length=50)
    email = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
