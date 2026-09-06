from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('project/create/', views.create_project, name='create_project'),
    path('project/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('project/delete/<int:project_id>/', views.delete_project, name='delete_project'),

    path('project/<int:project_id>/invite/', views.create_invitation, name='create_invitation'),
    path('invite/<str:token>/', views.accept_invitation, name='accept_invitation'),
    

    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/task/create/', views.create_task, name='create_task'),
    path('project/<int:project_id>/task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('project/<int:project_id>/task/<int:task_id>/delete/', views.delete_task, name='delete_task'),

    path('project/<int:project_id>/task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('project/<int:project_id>/task/<int:task_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('project/<int:project_id>/task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('project/<int:project_id>/task/<int:task_id>/update_status/', views.update_task_status, name='update_task_status'),

    path('project/<int:project_id>/collaborators/', views.manage_collaborators, name='manage_collaborators'),
    path('project/<int:project_id>/collaborators/<int:member_id>/update_role/', views.update_member_role, name='update_member_role'),
    path('project/<int:project_id>/collaborators/<int:member_id>/remove/', views.remove_member, name='remove_member'),
]