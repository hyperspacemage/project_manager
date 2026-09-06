import uuid
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .models import *


# --- AUTHENTICATION VIEWS ---

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        raw_password = request.POST.get('password')
        
        hashed_password = make_password(raw_password)
        
        new_user = User(
            username=username, 
            email=email, 
            password=hashed_password,
            created_at=timezone.now()
        )
        new_user.save()
        
        return redirect('login')
        
    return render(request, 'tasks/register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            if check_password(raw_password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                
                if 'pending_invite' in request.session:
                    token = request.session.pop('pending_invite')
                    return accept_invitation(request, token)
                    
                return redirect('dashboard')
            else:
                return render(request, 'tasks/login.html', {'error': 'Incorrect password.'})
        except User.DoesNotExist:
            return render(request, 'tasks/login.html', {'error': 'User does not exist.'})
            
    return render(request, 'tasks/login.html')


def logout_user(request):
    request.session.flush()
    return redirect('login')


# --- DASHBOARD & PROJECT VIEWS ---

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    current_user = User.objects.get(id=request.session['user_id'])
    user_memberships = ProjectMember.objects.filter(user=current_user).select_related('project', 'role')
    
    return render(request, 'tasks/dashboard.html', {
        'user': current_user, 
        'memberships': user_memberships
    })

def create_project(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        new_project = Project.objects.create(
            name=name, 
            description=description, 
            created_at=timezone.now()
        )
        
        owner_role = Role.objects.get(name='Owner')
        
        current_user = User.objects.get(id=request.session['user_id'])
        ProjectMember.objects.create(
            user=current_user,
            project=new_project,
            role=owner_role,
            joined_at=timezone.now()
        )
        
        return redirect('dashboard')
        
    return render(request, 'tasks/create_project.html')


def project_detail(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).select_related('role').first()
    
    if not membership:
        return redirect('dashboard')
        
    project = Project.objects.get(id=project_id)
    tasks = Task.objects.filter(project=project).select_related('priority', 'assigned_to')
    task_statuses = ['Pending', 'In Progress', 'Completed']
    
    return render(request, 'tasks/project_detail.html', {
        'project': project,
        'role': membership.role.name,
        'tasks': tasks,
        'statuses': task_statuses
    })




def edit_project(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    
    if not ProjectMember.objects.filter(user=current_user, project_id=project_id).exists():
        return redirect('dashboard')
        
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.save()
        return redirect('dashboard')
        
    return render(request, 'tasks/edit_project.html', {'project': project})


def delete_project(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    
    is_owner = ProjectMember.objects.filter(
        user=current_user, 
        project_id=project_id, 
        role__name='Owner'
    ).exists()
    if not is_owner:
        return redirect('dashboard')
        
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        project.delete()
        return redirect('dashboard')
        
    return render(request, 'tasks/delete_project.html', {'project': project})


# --- COLLABORATION & INVITATION VIEWS ---

def create_invitation(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    
    membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).select_related('role').first()
    
    if not membership or membership.role.name != 'Owner':
        return redirect('project_detail', project_id=project_id)
        
    project = Project.objects.get(id=project_id)
    token = str(uuid.uuid4())
    expires_at = timezone.now() + timedelta(days=1)
    
    Invitation.objects.create(
        project=project,
        inviter=current_user,
        token=token,
        expires_at=expires_at,
        created_at=timezone.now()
    )
    
    invite_url = request.build_absolute_uri(f'/invite/{token}/')
    
    return render(request, 'tasks/show_invite.html', {
        'project': project,
        'invite_url': invite_url
    })


def accept_invitation(request, token):
    try:
        invitation = Invitation.objects.get(token=token)
    except Invitation.DoesNotExist:
        return render(request, 'tasks/invite_error.html', {'message': 'The invitation link is invalid.'})
        
    if timezone.now() > invitation.expires_at:
        return render(request, 'tasks/invite_error.html', {'message': 'This invitation link has expired.'})
        
    if 'user_id' not in request.session:
        request.session['pending_invite'] = token
        return render(request, 'tasks/join_prompt.html', {'project': invitation.project})
        
    current_user = User.objects.get(id=request.session['user_id'])
    
    if not ProjectMember.objects.filter(user=current_user, project=invitation.project).exists():
        viewer_role = Role.objects.get(name='Viewer')
        
        ProjectMember.objects.create(
            user=current_user,
            project=invitation.project,
            role=viewer_role,
            joined_at=timezone.now()
        )
        
    return redirect('dashboard')


# --- TASK MANAGEMENT VIEWS ---

def create_task(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).first()
    
    if not membership or membership.role.name == 'Viewer':
        return redirect('project_detail', project_id=project_id)
        
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority_id = request.POST.get('priority')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        priority = Priority.objects.get(id=priority_id) if priority_id else None
        assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None
        
        Task.objects.create(
            project=project,
            title=title,
            description=description,
            status='Pending',
            priority=priority,
            created_by=current_user,
            assigned_to=assigned_to,
            due_date=due_date if due_date else None,
            created_at=timezone.now()
        )
        return redirect('project_detail', project_id=project.id)

    priorities = Priority.objects.all()
    members = User.objects.filter(projectmember__project=project)
    
    return render(request, 'tasks/create_task.html', {
        'project': project,
        'priorities': priorities,
        'members': members
    })

def edit_task(request, project_id, task_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).first()
    
    # Permission Check: Viewers cannot edit tasks
    if not membership or membership.role.name == 'Viewer':
        return redirect('project_detail', project_id=project_id)
        
    task = Task.objects.get(id=task_id, project_id=project_id)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.status = request.POST.get('status')
        
        priority_id = request.POST.get('priority')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        task.priority = Priority.objects.get(id=priority_id) if priority_id else None
        task.assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None
        task.due_date = due_date if due_date else None
        
        task.updated_at = timezone.now()
        task.save()
        return redirect('project_detail', project_id=project_id)
        
    priorities = Priority.objects.all()
    members = User.objects.filter(projectmember__project_id=project_id)
    formatted_due_date = task.due_date.strftime('%Y-%m-%dT%H:%M') if task.due_date else ''
    
    return render(request, 'tasks/edit_task.html', {
        'project_id': project_id,
        'task': task,
        'priorities': priorities,
        'members': members,
        'formatted_due_date': formatted_due_date,
        'statuses': ['Pending', 'In Progress', 'Completed']
    })


def delete_task(request, project_id, task_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    current_user = User.objects.get(id=request.session['user_id'])
    membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).first()
    
    # Permission Check: Viewers cannot delete tasks
    if not membership or membership.role.name == 'Viewer':
        return redirect('project_detail', project_id=project_id)
        
    task = Task.objects.get(id=task_id, project_id=project_id)
    
    if request.method == 'POST':
        task.delete()
        return redirect('project_detail', project_id=project_id)
        
    return render(request, 'tasks/delete_task.html', {
        'project_id': project_id,
        'task': task
    })

def add_comment(request, project_id, task_id):
    if request.method == 'POST' and 'user_id' in request.session:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                task_id=task_id,
                user_id=request.session['user_id'],
                content=content,
                created_at=timezone.now()
            )
    return redirect('task_detail', project_id=project_id, task_id=task_id)

def delete_comment(request, project_id, task_id, comment_id):
    if request.method == 'POST' and 'user_id' in request.session:
        try:
            comment = Comment.objects.get(id=comment_id, task_id=task_id)
            if comment.user_id == request.session['user_id']:
                comment.delete()
        except Comment.DoesNotExist:
            pass
            
    return redirect('task_detail', project_id=project_id, task_id=task_id)

def task_detail(request, project_id, task_id):
    if 'user_id' not in request.session:
        return redirect('login')
        
    task = Task.objects.select_related('priority', 'assigned_to').get(id=task_id, project_id=project_id)
    
    comments = Comment.objects.filter(task=task).select_related('user').order_by('-created_at')
    
    return render(request, 'tasks/task_detail.html', {
        'task': task, 
        'comments': comments,
        'project_id': project_id
    })

def update_task_status(request, project_id, task_id):
    if request.method == 'POST' and 'user_id' in request.session:
        try:
            task = Task.objects.get(id=task_id, project_id=project_id)
            new_status = request.POST.get('status')
            
            if new_status:
                task.status = new_status
                task.updated_at = timezone.now()
                task.save()
        except Task.DoesNotExist:
            pass
            
    return redirect('project_detail', project_id=project_id)

# --- Collaborator Management Views ---

def manage_collaborators(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = User.objects.get(id=request.session['user_id'])
    current_membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).select_related('role').first()

    if not current_membership or current_membership.role.name not in ['Owner', 'Admin']:
        return redirect('project_detail', project_id=project_id)

    project = Project.objects.get(id=project_id)
    members = ProjectMember.objects.filter(project=project).select_related('user', 'role')
    roles = Role.objects.all()

    return render(request, 'tasks/manage_collaborators.html', {
        'project': project,
        'members': members,
        'roles': roles,
        'current_user_id': current_user.id
    })


def update_member_role(request, project_id, member_id):
    if request.method == 'POST' and 'user_id' in request.session:
        current_user = User.objects.get(id=request.session['user_id'])
        current_membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).select_related('role').first()

        if current_membership and current_membership.role.name in ['Owner', 'Admin']:
            new_role_id = request.POST.get('role_id')
            member_to_update = ProjectMember.objects.filter(id=member_id, project_id=project_id).first()
            
            if member_to_update and member_to_update.user_id != current_user.id:
                member_to_update.role_id = new_role_id
                member_to_update.save()

    return redirect('manage_collaborators', project_id=project_id)


def remove_member(request, project_id, member_id):
    if request.method == 'POST' and 'user_id' in request.session:
        current_user = User.objects.get(id=request.session['user_id'])
        current_membership = ProjectMember.objects.filter(user=current_user, project_id=project_id).select_related('role').first()

        if current_membership and current_membership.role.name in ['Owner', 'Admin']:
            member_to_remove = ProjectMember.objects.filter(id=member_id, project_id=project_id).first()
            
            if member_to_remove and member_to_remove.user_id != current_user.id:
                member_to_remove.delete()

    return redirect('manage_collaborators', project_id=project_id)