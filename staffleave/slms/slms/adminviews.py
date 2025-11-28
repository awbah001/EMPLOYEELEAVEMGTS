
from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import  logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser,Staff,Staff_Leave,Department,DepartmentHead,SystemSettings
from django.db.models import Q
from .decorators import admin_required

@login_required(login_url='/')
@admin_required
def HOME(request):
    """Admin Dashboard - Combined admin and super admin functionality"""
    staff_count = Staff.objects.all().count()
    leave_count = Staff_Leave.objects.all().count()
    total_users = CustomUser.objects.count()
    total_departments = Department.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    
    context = {
        'staff_count': staff_count,
        'leave_count': leave_count,
        'total_users': total_users,
        'total_departments': total_departments,
        'active_users': active_users,
    }
    return render(request,'admin/home.html',context)


@login_required(login_url='/')
def ADD_STAFF(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        user_role = request.POST.get('user_role', '2')
        staff_type = request.POST.get('staff_type', '')
        department_id = request.POST.get('department', '')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request,'Email is already Exist')
            return redirect('add_staff')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request,'Username is already Exist')
            return redirect('add_staff')
        
        else:
            user = CustomUser(
                first_name = first_name,
                last_name = last_name,
                email = email,
                profile_pic = profile_pic,
                user_type = user_role,
                username = username
            )
            user.set_password(password)
            user.save()

            if user_role == '2':  # Staff
                department = None
                if department_id:
                    try:
                        department = Department.objects.get(id=department_id)
                    except Department.DoesNotExist:
                        pass
                
                staff = Staff(
                    admin = user,
                    address = address,
                    gender = gender,
                    staff_type = staff_type if staff_type else None,
                    department = department
                )
                staff.save()
                messages.success(request,'Staff member has been added successfully.')
            elif user_role == '3':  # Department Head
                # Create DepartmentHead record
                department = None
                if department_id:
                    try:
                        department = Department.objects.get(id=department_id)
                        DepartmentHead.objects.get_or_create(
                            admin=user,
                            defaults={'department': department}
                        )
                        messages.success(request,'Department Head has been added successfully.')
                    except Department.DoesNotExist:
                        messages.warning(request,'Department not found. User created but Department Head record not created. Please assign department later.')
                else:
                    messages.warning(request,'Department Head created but no department assigned. Please assign department later.')
            elif user_role == '4':  # HR
                messages.success(request,'HR user has been added successfully.')
            else:  # Super Admin or other
                messages.success(request,'User has been added successfully.')
            return redirect('add_staff')

    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request,'admin/add_staff.html', context)

@login_required(login_url='/')
def VIEW_STAFF(request):
    staff = Staff.objects.all()
    context = {
        "staff":staff,
    }
    return render(request,'admin/view_staff.html',context)

@login_required(login_url='/')
def EDIT_STAFF(request,id):
    staff = Staff.objects.get(id = id)
    # Prevent admin user edit through staff edit page
    if staff.admin.user_type == '1':
        messages.error(request, 'You cannot edit an admin using this page.')
        return redirect('view_staff')
    context = {
        "staff":staff,
    }
    return render(request,'admin/edit_staff.html',context)

@login_required(login_url='/')
def UPDATE_STAFF(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        user = CustomUser.objects.get(id = staff_id)
        # Prevent admin user update through staff update page
        if user.user_type == '1':
            messages.error(request, 'You cannot update an admin using this page.')
            return redirect('view_staff')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        staff_type = request.POST.get('staff_type', '')
        user.username =username
        user.first_name =first_name
        user.last_name =last_name
        user.email =email
        if password != None and password !="":
            user.set_password(password)
        if profile_pic != None and profile_pic !="":
            user.profile_pic = profile_pic
        user.save()
        staff = Staff.objects.get(admin = staff_id)
        staff.gender = gender
        staff.address = address
        if staff_type:
            staff.staff_type = staff_type
        staff.save()
        messages.success(request,'Staf details has been succeesfully updated')
        return redirect('view_staff')
    return render(request,'admin/edit_staff.html')                                                

@login_required(login_url='/')
def DELETE_STAFF(request,admin):
    staff = CustomUser.objects.get(id = admin)
    staff.delete()
    messages.success(request,"Staff record has been deleted successfully.")
    return redirect('view_staff')


@login_required(login_url='/')
def STAFF_LEAVE_VIEW(request):
    staff_leave = Staff_Leave.objects.all()
    context = {
        "staff_leave":staff_leave,
    }
    
    return render(request,'admin/staff_leave.html',context)

@login_required(login_url='/')
def STAFF_APPROVE_LEAVE(request,id):
    leave = Staff_Leave.objects.get(id = id)
    leave.status = 1
    leave.save()
    
    # Update leave balance automatically
    from .leave_utils import update_leave_balance_on_approval
    update_leave_balance_on_approval(leave)
    
    messages.success(request, 'Leave application approved successfully.')
    return redirect('staff_leave_view_admin')

@login_required(login_url='/')
def STAFF_DISAPPROVE_LEAVE(request,id):
    leave = Staff_Leave.objects.get(id = id)
    leave.status = 2
    leave.save()
    return redirect('staff_leave_view_admin')


# ========== Super Admin Functions (Now Admin Functions) ==========

@login_required(login_url='/')
@admin_required
def MANAGE_USERS(request):
    """Unified user management: Create, edit, assign roles in one place"""
    users = CustomUser.objects.all().select_related('staff').order_by('-date_joined')
    departments = Department.objects.all()
    
    # Handle POST requests (create, update, assign role)
    if request.method == "POST":
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action == 'create':
            # Create new user
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_type = request.POST.get('user_type', '2')
            is_active = request.POST.get('is_active') == 'on'
            profile_pic = request.FILES.get('profile_pic')
            
            if CustomUser.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exists')
            elif CustomUser.objects.filter(username=username).exists():
                messages.warning(request, 'Username already exists')
            else:
                user = CustomUser(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    user_type=user_type,
                    is_active=is_active,
                    profile_pic=profile_pic
                )
                user.set_password(password)
                user.save()
                
                # If creating Department Head, create DepartmentHead record
                if user_type == '3':
                    department_id = request.POST.get('department_id')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            DepartmentHead.objects.get_or_create(
                                admin=user,
                                defaults={'department': department}
                            )
                            messages.success(request, f'Department Head created successfully and assigned to {department.name}')
                        except Department.DoesNotExist:
                            messages.warning(request, 'User created but department not found.')
                    else:
                        messages.warning(request, 'Department Head created but no department assigned.')
                elif user_type == '4':
                    messages.success(request, 'HR user created successfully')
                else:
                    messages.success(request, 'User created successfully')
        
        elif action == 'update' and user_id:
            # Update existing user
            try:
                user = CustomUser.objects.get(id=user_id)
                old_user_type = user.user_type
                
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.email = request.POST.get('email')
                user.username = request.POST.get('username')
                new_user_type = request.POST.get('user_type')
                user.user_type = new_user_type
                user.is_active = request.POST.get('is_active') == 'on'
                
                password = request.POST.get('password')
                if password:
                    user.set_password(password)
                
                profile_pic = request.FILES.get('profile_pic')
                if profile_pic:
                    user.profile_pic = profile_pic
                
                user.save()
                
                # Handle Department Head role changes
                if new_user_type == '3':
                    department_id = request.POST.get('department_id')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            DepartmentHead.objects.update_or_create(
                                admin=user,
                                defaults={'department': department}
                            )
                        except Department.DoesNotExist:
                            messages.warning(request, 'Department not found.')
                    elif old_user_type != '3':
                        messages.warning(request, 'Department Head role assigned but no department selected.')
                elif old_user_type == '3' and new_user_type != '3':
                    DepartmentHead.objects.filter(admin=user).delete()
                
                messages.success(request, 'User updated successfully')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found')
        
        elif action == 'assign_role' and user_id:
            # Quick role assignment
            try:
                user = CustomUser.objects.get(id=user_id)
                old_user_type = user.user_type
                new_user_type = request.POST.get('user_type')
                department_id = request.POST.get('department_id')
                
                user.user_type = new_user_type
                user.save()
                
                # Handle Department Head role
                if new_user_type == '3' and department_id:
                    department = Department.objects.get(id=department_id)
                    DepartmentHead.objects.get_or_create(
                        admin=user,
                        defaults={'department': department}
                    )
                elif old_user_type == '3' and new_user_type != '3':
                    DepartmentHead.objects.filter(admin=user).delete()
                
                messages.success(request, f'Role assigned successfully to {user.username}')
            except Exception as e:
                messages.error(request, f'Error assigning role: {str(e)}')
        
        return redirect('admin_manage_users')
    
    # Handle GET requests
    user_type_filter = request.GET.get('user_type', '')
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # Get user for editing if provided
    edit_user = None
    edit_user_department = None
    edit_user_id = request.GET.get('edit', '')
    if edit_user_id:
        try:
            edit_user = CustomUser.objects.get(id=edit_user_id)
            if edit_user.user_type == '3':
                try:
                    dept_head = DepartmentHead.objects.get(admin=edit_user)
                    edit_user_department = dept_head.department
                except DepartmentHead.DoesNotExist:
                    pass
        except CustomUser.DoesNotExist:
            pass
    
    context = {
        'users': users,
        'user_type_filter': user_type_filter,
        'departments': departments,
        'edit_user': edit_user,
        'edit_user_department': edit_user_department,
    }
    return render(request, 'admin/manage_users.html', context)


@login_required(login_url='/')
@admin_required
def CREATE_USER(request):
    """Create new user account"""
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', '2')
        is_active = request.POST.get('is_active') == 'on'
        profile_pic = request.FILES.get('profile_pic')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return redirect('admin_create_user')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            return redirect('admin_create_user')
        
        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            user_type=user_type,
            is_active=is_active,
            profile_pic=profile_pic
        )
        user.set_password(password)
        user.save()
        
        # If creating Department Head, create DepartmentHead record
        if user_type == '3':  # Department Head
            department_id = request.POST.get('department_id')
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                    DepartmentHead.objects.get_or_create(
                        admin=user,
                        defaults={'department': department}
                    )
                    messages.success(request, f'Department Head created successfully and assigned to {department.name}')
                except Department.DoesNotExist:
                    messages.warning(request, 'User created but department not found. Please assign department later.')
            else:
                messages.warning(request, 'Department Head created but no department assigned. Please assign department later.')
        elif user_type == '4':  # HR
            messages.success(request, 'HR user created successfully')
        else:
            messages.success(request, 'User created successfully')
        
        return redirect('admin_manage_users')
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'admin/create_user.html', context)


@login_required(login_url='/')
@admin_required
def EDIT_USER(request, id):
    """Edit user account"""
    user = get_object_or_404(CustomUser, id=id)
    
    if request.method == "POST":
        old_user_type = user.user_type
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        new_user_type = request.POST.get('user_type')
        user.user_type = new_user_type
        user.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            user.profile_pic = profile_pic
        
        user.save()
        
        # Handle Department Head role changes
        if new_user_type == '3':  # Department Head
            department_id = request.POST.get('department_id')
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                    DepartmentHead.objects.update_or_create(
                        admin=user,
                        defaults={'department': department}
                    )
                except Department.DoesNotExist:
                    messages.warning(request, 'Department not found. Department Head record not updated.')
            elif old_user_type != '3':
                # User was just assigned Department Head role but no department selected
                messages.warning(request, 'Department Head role assigned but no department selected. Please assign department.')
        elif old_user_type == '3' and new_user_type != '3':
            # User was Department Head but role changed - remove DepartmentHead record
            DepartmentHead.objects.filter(admin=user).delete()
        
        messages.success(request, 'User updated successfully')
        return redirect('admin_manage_users')
    
    # Get department if user is Department Head
    department = None
    if user.user_type == '3':
        try:
            dept_head = DepartmentHead.objects.get(admin=user)
            department = dept_head.department
        except DepartmentHead.DoesNotExist:
            pass
    
    departments = Department.objects.all()
    context = {
        'user': user,
        'departments': departments,
        'current_department': department,
    }
    return render(request, 'admin/edit_user.html', context)


@login_required(login_url='/')
@admin_required
def DEACTIVATE_USER(request, id):
    """Deactivate user account"""
    user = get_object_or_404(CustomUser, id=id)
    
    if user.id == request.user.id:
        messages.error(request, 'You cannot deactivate your own account')
        return redirect('admin_manage_users')
    
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been deactivated')
    return redirect('admin_manage_users')


@login_required(login_url='/')
@admin_required
def ACTIVATE_USER(request, id):
    """Activate user account"""
    user = get_object_or_404(CustomUser, id=id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been activated')
    return redirect('admin_manage_users')


@login_required(login_url='/')
@admin_required
def DELETE_USER(request, id):
    """Delete user account"""
    user = get_object_or_404(CustomUser, id=id)
    
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account')
        return redirect('admin_manage_users')
    
    username = user.username
    user.delete()
    messages.success(request, f'User {username} has been deleted')
    return redirect('admin_manage_users')


@login_required(login_url='/')
@admin_required
def ASSIGN_ROLES(request):
    """Assign roles to users"""
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')
        department_id = request.POST.get('department_id')
        
        try:
            user = CustomUser.objects.get(id=user_id)
            user.user_type = user_type
            user.save()
            
            # If assigning Department Head role, create DepartmentHead record
            if user_type == '3' and department_id:
                department = Department.objects.get(id=department_id)
                DepartmentHead.objects.get_or_create(
                    admin=user,
                    defaults={'department': department}
                )
            
            messages.success(request, f'Role assigned successfully to {user.username}')
        except Exception as e:
            messages.error(request, f'Error assigning role: {str(e)}')
        
        return redirect('admin_assign_roles')
    
    users = CustomUser.objects.all()
    departments = Department.objects.all()
    
    context = {
        'users': users,
        'departments': departments,
    }
    return render(request, 'admin/assign_roles.html', context)


@login_required(login_url='/')
@admin_required
def MANAGE_DEPARTMENTS(request):
    """Manage departments"""
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Department.objects.filter(name=name).exists():
            messages.warning(request, 'Department with this name already exists')
        else:
            Department.objects.create(name=name, description=description)
            messages.success(request, 'Department created successfully')
        
        return redirect('admin_manage_departments')
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'admin/manage_departments.html', context)


@login_required(login_url='/')
@admin_required
def UPDATE_DEPARTMENT(request, id):
    """Update department"""
    department = get_object_or_404(Department, id=id)
    
    if request.method == "POST":
        department.name = request.POST.get('name')
        department.description = request.POST.get('description')
        department.save()
        messages.success(request, 'Department updated successfully')
        return redirect('admin_manage_departments')
    
    context = {'department': department}
    return render(request, 'admin/update_department.html', context)


@login_required(login_url='/')
@admin_required
def DELETE_DEPARTMENT(request, id):
    """Delete department"""
    department = get_object_or_404(Department, id=id)
    department_name = department.name
    department.delete()
    messages.success(request, f'Department {department_name} deleted successfully')
    return redirect('admin_manage_departments')


@login_required(login_url='/')
@admin_required
def SYSTEM_SETTINGS(request):
    """Manage system-wide settings"""
    if request.method == "POST":
        key = request.POST.get('key')
        value = request.POST.get('value')
        description = request.POST.get('description')
        
        setting, created = SystemSettings.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        
        if not created:
            setting.value = value
            setting.description = description
            setting.save()
        
        messages.success(request, 'Setting saved successfully')
        return redirect('admin_system_settings')
    
    settings = SystemSettings.objects.all()
    context = {'settings': settings}
    return render(request, 'admin/system_settings.html', context)


@login_required(login_url='/')
@admin_required
def UPDATE_SETTING(request, id):
    """Update system setting"""
    setting = get_object_or_404(SystemSettings, id=id)
    
    if request.method == "POST":
        setting.value = request.POST.get('value')
        setting.description = request.POST.get('description')
        setting.save()
        messages.success(request, 'Setting updated successfully')
        return redirect('admin_system_settings')
    
    context = {'setting': setting}
    return render(request, 'admin/update_setting.html', context)


@login_required(login_url='/')
@admin_required
def AUTH_CONFIGURATION(request):
    """Configure authentication settings (Google login, SSO, etc.)"""
    if request.method == "POST":
        # Save authentication settings
        google_enabled = request.POST.get('google_enabled') == 'on'
        sso_enabled = request.POST.get('sso_enabled') == 'on'
        google_client_id = request.POST.get('google_client_id', '')
        google_client_secret = request.POST.get('google_client_secret', '')
        
        # Save to SystemSettings
        SystemSettings.objects.update_or_create(
            key='google_auth_enabled',
            defaults={'value': str(google_enabled), 'description': 'Enable Google OAuth login'}
        )
        SystemSettings.objects.update_or_create(
            key='sso_enabled',
            defaults={'value': str(sso_enabled), 'description': 'Enable SSO authentication'}
        )
        SystemSettings.objects.update_or_create(
            key='google_client_id',
            defaults={'value': google_client_id, 'description': 'Google OAuth Client ID'}
        )
        SystemSettings.objects.update_or_create(
            key='google_client_secret',
            defaults={'value': google_client_secret, 'description': 'Google OAuth Client Secret'}
        )
        
        messages.success(request, 'Authentication configuration saved successfully')
        return redirect('admin_auth_config')
    
    # Get current settings
    google_enabled = SystemSettings.objects.filter(key='google_auth_enabled').first()
    sso_enabled = SystemSettings.objects.filter(key='sso_enabled').first()
    google_client_id = SystemSettings.objects.filter(key='google_client_id').first()
    google_client_secret = SystemSettings.objects.filter(key='google_client_secret').first()
    
    context = {
        'google_enabled': google_enabled.value if google_enabled else 'False',
        'sso_enabled': sso_enabled.value if sso_enabled else 'False',
        'google_client_id': google_client_id.value if google_client_id else '',
        'google_client_secret': google_client_secret.value if google_client_secret else '',
    }
    return render(request, 'admin/auth_configuration.html', context)



