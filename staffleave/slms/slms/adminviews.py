
from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import  logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser,Employee,Employee_Leave,Department,DepartmentHead,SystemSettings,PublicHoliday,CalendarEvent
from .auth_utils import validate_password, get_int_setting
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.db.models import Q
from .decorators import admin_required
from datetime import date, timedelta
from calendar import monthrange

@login_required(login_url='/')
@admin_required
def HOME(request):
    """Admin Dashboard - Combined admin and super admin functionality"""
    # Count employees who are CustomUser type '2' (employees)
    staff_count = Employee.objects.filter(admin__user_type='2').count()
    leave_count = Employee_Leave.objects.all().count()
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
    # Consolidate creation into the Admin CREATE_USER handler.
    # - GET requests are redirected to the canonical Admin create user page
    # - POST requests are delegated to CREATE_USER so there is a single source of truth
    if request.method == "POST":
        # Delegate POST handling to the CREATE_USER function (keeps same behaviour)
        return CREATE_USER(request)

    # Redirect GET requests to the canonical admin create user UI
    return redirect('admin_create_user')

@login_required(login_url='/')
def VIEW_STAFF(request):
    # Show all system users for Admin "View Users" — previously this page listed Employee records only.
    user_type = request.GET.get('user_type')
    
    if user_type:
        # Filter by user_type if provided
        users = CustomUser.objects.filter(user_type=user_type).order_by('-date_joined')
    else:
        # Show all users if no filter specified
        users = CustomUser.objects.all().order_by('-date_joined')
    
    context = {
        "users": users,
    }
    return render(request,'admin/view_staff.html',context)

@login_required(login_url='/')
def EDIT_STAFF(request,id):
    employee = Employee.objects.get(id = id)
    # Prevent admin user edit through staff edit page
    if employee.admin.user_type == '1':
        messages.error(request, 'You cannot edit an admin using this page.')
        return redirect('view_staff')
    departments = Department.objects.all()
    context = {
        "employee":staff,
        "departments": departments,
    }
    return render(request,'admin/edit_staff.html',context)

@login_required(login_url='/')
def UPDATE_STAFF(request):
    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        user = CustomUser.objects.get(id = employee_id)
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
        employee_type = request.POST.get('employee_type', '')
        user.username =username
        user.first_name =first_name
        user.last_name =last_name
        user.email =email
        if password is not None and password != "":
            ok, msg = validate_password(password)
            if not ok:
                messages.warning(request, msg)
                return redirect('view_staff')
            user.set_password(password)
        if profile_pic != None and profile_pic !="":
            user.profile_pic = profile_pic
        user.save()
        employee = Employee.objects.get(admin = employee_id)
        employee.gender = gender
        employee.address = address
        if employee_type:
            employee.employee_type = employee_type
        
        # Handle department update
        department_id = request.POST.get('department')
        if department_id:
            try:
                employee.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                pass
        elif department_id == '':
            # If empty string, remove department assignment
            employee.department = None
        
        employee.save()
        messages.success(request,'Staf details has been succeesfully updated')
        return redirect('view_staff')
    return render(request,'admin/edit_staff.html')                                                

@login_required(login_url='/')
def DELETE_STAFF(request,admin):
    staff = CustomUser.objects.get(id = admin)
    staff.delete()
    messages.success(request,"Employee record has been deleted successfully.")
    return redirect('view_staff')


@login_required(login_url='/')
@login_required(login_url='/')
@admin_required
def STAFF_LEAVE_VIEW(request):
    all_leaves = Employee_Leave.objects.all().order_by('-created_at')
    
    # Get filter parameter from GET request
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'pending':
        staff_leave = all_leaves.filter(status=0)
    elif status_filter == 'approved':
        staff_leave = all_leaves.filter(status=1)
    elif status_filter == 'rejected':
        staff_leave = all_leaves.filter(status=2)
    else:
        staff_leave = all_leaves
    
    # Calculate status counts (always from all leaves)
    total_count = all_leaves.count()
    pending_count = all_leaves.filter(status=0).count()
    approved_count = all_leaves.filter(status=1).count()
    rejected_count = all_leaves.filter(status=2).count()
    
    context = {
        "employee_leave": staff_leave,
        "total_count": total_count,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "status_filter": status_filter,
    }
    
    return render(request,'admin/staff_leave.html',context)

@login_required(login_url='/')
def STAFF_APPROVE_LEAVE(request,id):
    leave = Employee_Leave.objects.get(id = id)
    leave.status = 1
    leave.save()
    
    # Update leave balance automatically
    from .leave_utils import update_leave_balance_on_approval
    update_leave_balance_on_approval(leave)
    
    messages.success(request, 'Leave application approved successfully.')
    return redirect('staff_leave_view_admin')

@login_required(login_url='/')
@admin_required
def STAFF_DISAPPROVE_LEAVE(request,id):
    leave = Employee_Leave.objects.get(id = id)
    leave.status = 2
    leave.save()
    messages.success(request, 'Leave application rejected successfully.')
    return redirect('staff_leave_view_admin')


# ========== Super Admin Functions (Now Admin Functions) ==========

@login_required(login_url='/')
@admin_required
def MANAGE_USERS(request):
    """Unified user management: Create, edit, assign roles in one place"""
    users = CustomUser.objects.all().select_related('employee').order_by('date_joined')
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
                # validate password before creating
                ok, msg = validate_password(password)
                if not ok:
                    messages.warning(request, msg)
                    return redirect('admin_manage_users')

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
                            # Check if this department already has a department head
                            if DepartmentHead.objects.filter(department=department).exists():
                                user.delete()  # Remove the user that was just created
                                messages.error(request, f'A department head already exists for {department.name}. Cannot create another one.')
                                return redirect('admin_manage_users')
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

                # Optionally create minimal staff profile for Employee accounts
                if user_type == '2' and request.POST.get('create_staff_profile') == 'on':
                    employee_id = request.POST.get('employee_id', '').strip()
                    defaults = {}
                    if employee_id:
                        defaults['employee_id'] = employee_id
                    # employee_id will be auto-generated in save() if not provided
                    try:
                        Employee.objects.get_or_create(admin=user, defaults=defaults)
                    except Exception as e:
                        messages.warning(request, f'Failed to create staff profile: {str(e)}')
        
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
                    ok, msg = validate_password(password)
                    if not ok:
                        messages.warning(request, msg)
                        return redirect('admin_manage_users')
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
                            # Check if another department head already exists for this department
                            # Allow if the user is already the department head for this department
                            existing_head = DepartmentHead.objects.filter(
                                department=department
                            ).exclude(admin=user).first()
                            
                            if existing_head:
                                messages.error(request, f'A department head already exists for {department.name}. Cannot assign another one.')
                                return redirect('admin_manage_users')
                            
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

                # If user changed to Employee and requested, ensure a Employee profile exists
                    employee_id = request.POST.get('employee_id', '').strip()
                    defaults = {}
                    if employee_id:
                        defaults['employee_id'] = employee_id
                    # employee_id will be auto-generated in save() if not provided
                    try:
                        Employee.objects.get_or_create(admin=user, defaults=defaults)
                    except Exception as e:
                        messages.warning(request, f'Failed to create staff profile: {str(e)}')
                
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
        'edit_user_staff': getattr(edit_user, 'employee', None) if edit_user else None,
        'edit_user_department': edit_user_department,
        'departments_with_heads': DepartmentHead.objects.values('department_id'),
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
        
        # validate password rules on creation from create_user form
        ok, msg = validate_password(password)
        if not ok:
            messages.warning(request, msg)
            return redirect('admin_create_user')

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
                    # Check if this department already has a department head
                    if DepartmentHead.objects.filter(department=department).exists():
                        user.delete()  # Remove the user that was just created
                        messages.error(request, f'A department head already exists for {department.name}. Cannot create another one.')
                        return redirect('admin_create_user')
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

        # Create Employee profile when creating a Employee account or if create_staff_profile is checked
        if (user_type == '2' or request.POST.get('create_staff_profile') == 'on'):
            employee_id = request.POST.get('employee_id', '')
            phone_number = request.POST.get('phone_number', '')
            address = request.POST.get('address', '')
            gender = request.POST.get('gender', '')
            date_of_joining = request.POST.get('date_of_joining') or None
            employee_type = request.POST.get('employee_type', 'Full-time')
            department_id = request.POST.get('department_id') or None
            
            # Parse date_of_joining if provided
            date_joined_obj = None
            if date_of_joining:
                try:
                    from datetime import datetime
                    date_joined_obj = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
                except:
                    pass
            
            # Get department if provided
            department = None
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    pass
            
            try:
                # Create Employee record with all information
                staff_defaults = {
                    'phone_number': phone_number if phone_number else None,
                    'address': address if address else 'Not provided',
                    'gender': gender if gender else 'Not specified',
                    'employee_type': employee_type if employee_type else 'Full-time',
                    'department': department,
                }
                
                # Employee ID will be auto-generated if not provided
                if employee_id and employee_id.strip():
                    staff_defaults['employee_id'] = employee_id
                if date_joined_obj:
                    staff_defaults['date_of_joining'] = date_joined_obj
                
                Employee.objects.get_or_create(admin=user, defaults=staff_defaults)
                messages.success(request, 'User created successfully with staff profile')
            except Exception as e:
                # Non-fatal, inform admin
                messages.warning(request, f'Employee profile creation failed: {str(e)}')
        
        return redirect('admin_manage_users')
    
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'departments_with_heads': DepartmentHead.objects.values('department_id'),
    }
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
            ok, msg = validate_password(password)
            if not ok:
                messages.warning(request, msg)
                return redirect('admin_edit_user', id=id)
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

        # If user changed to Employee, and admin requested, ensure Employee profile exists
        if new_user_type == '2' and request.POST.get('create_staff_profile') == 'on':
            employee_id = request.POST.get('employee_id', '').strip()
            defaults = {}
            if employee_id:
                defaults['employee_id'] = employee_id
            # employee_id will be auto-generated in save() if not provided
            try:
                Employee.objects.get_or_create(admin=user, defaults=defaults)
            except Exception as e:
                messages.warning(request, f'Could not create staff profile: {str(e)}')
        
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
def GENERATE_PASSWORD_RESET_LINK(request, id):
    """Admins can generate a password reset URL for a user (useful when email delivery is not possible).
    This returns a page showing the one-time reset link that can be copied and delivered to the user.
    """
    user = get_object_or_404(CustomUser, id=id)

    # Create uid and token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    reset_url = request.build_absolute_uri(reset_path)

    context = {
        'user': user,
        'reset_url': reset_url,
        'token_expires_minutes': int(get_int_setting('password_reset_timeout_minutes', 1440)) if get_int_setting('password_reset_timeout_minutes', None) else 1440
    }
    return render(request, 'admin/show_reset_link.html', context)


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
        # Support either single-key form or section forms
        section = request.POST.get('section', '').lower()

        if section == 'general':
            # Save multiple general settings
            company_name = request.POST.get('company_name', '')
            timezone = request.POST.get('timezone', '')
            working_days = request.POST.get('working_days_per_week', '')
            maintenance_mode = request.POST.get('maintenance_mode') == 'on'

            SystemSettings.objects.update_or_create(
                key='company_name', defaults={'value': company_name, 'description': 'Company display name'}
            )
            SystemSettings.objects.update_or_create(
                key='timezone', defaults={'value': timezone, 'description': 'System timezone'}
            )
            # validate working_days
            try:
                wd = int(working_days) if working_days != '' else 5
                if wd < 0 or wd > 7:
                    messages.warning(request, 'Working days must be between 0 and 7. Using default 5.')
                    wd = 5
            except Exception:
                messages.warning(request, 'Invalid working days value. Using default 5.')
                wd = 5

            SystemSettings.objects.update_or_create(
                key='working_days_per_week', defaults={'value': str(wd), 'description': 'Working days per week'}
            )
            SystemSettings.objects.update_or_create(
                key='maintenance_mode', defaults={'value': str(maintenance_mode), 'description': 'Maintenance mode on/off'}
            )

            messages.success(request, 'General settings saved successfully')
            return redirect('admin_system_settings')

        elif section == 'leave_policies':
            # Example leave policy fields; keep flexible
            carryover = request.POST.get('carryover_days', '')
            max_sick = request.POST.get('max_sick_per_year', '')

            try:
                c = int(carryover) if carryover != '' else 0
                if c < 0:
                    messages.warning(request, 'Carryover cannot be negative. Using 0.')
                    c = 0
            except Exception:
                messages.warning(request, 'Invalid carryover value. Using 0.')
                c = 0

            try:
                s = int(max_sick) if max_sick != '' else 10
                if s < 0:
                    messages.warning(request, 'Max sick leaves cannot be negative. Using 10.')
                    s = 10
            except Exception:
                messages.warning(request, 'Invalid sick leave value. Using 10.')
                s = 10
            SystemSettings.objects.update_or_create(
                key='leave_carryover_days', defaults={'value': str(carryover), 'description': 'Max leave carryover days'}
            )
            SystemSettings.objects.update_or_create(
                key='leave_max_sick_per_year', defaults={'value': str(max_sick), 'description': 'Max sick leave per year'}
            )
            messages.success(request, 'Leave policy settings saved')
            return redirect('admin_system_settings')

        elif section == 'notifications':
            email_enabled = request.POST.get('email_notifications') == 'on'
            sender = request.POST.get('email_sender', '')
            SystemSettings.objects.update_or_create(
                key='email_notifications_enabled', defaults={'value': str(email_enabled), 'description': 'Enable/disable email notifications'}
            )
            SystemSettings.objects.update_or_create(
                key='email_sender_address', defaults={'value': sender, 'description': 'Sender email address for notifications'}
            )
            messages.success(request, 'Notification settings saved')
            return redirect('admin_system_settings')

        elif section == 'security':
            password_min = request.POST.get('password_min_length', '')
            require_2fa = request.POST.get('require_2fa') == 'on'

            try:
                pmin = int(password_min) if password_min != '' else 8
                if pmin < 4:
                    messages.warning(request, 'Password minimum is too low; setting minimum to 4')
                    pmin = 4
            except Exception:
                messages.warning(request, 'Invalid password minimum; using default 8')
                pmin = 8
            SystemSettings.objects.update_or_create(
                key='password_min_length', defaults={'value': str(pmin), 'description': 'Minimum password length'}
            )
            SystemSettings.objects.update_or_create(
                key='require_2fa', defaults={'value': str(require_2fa), 'description': 'Require 2FA for logins'}
            )
            # Login lockout configuration
            login_lockout_threshold = request.POST.get('login_lockout_threshold', '')
            login_lockout_minutes = request.POST.get('login_lockout_minutes', '')

            try:
                lt = int(login_lockout_threshold) if login_lockout_threshold != '' else 5
                if lt < 1:
                    messages.warning(request, 'Lockout threshold must be at least 1. Using default 5.')
                    lt = 5
            except Exception:
                messages.warning(request, 'Invalid lockout threshold value; using default 5')
                lt = 5

            try:
                lm = int(login_lockout_minutes) if login_lockout_minutes != '' else 15
                if lm < 1:
                    messages.warning(request, 'Lockout minutes must be at least 1. Using default 15.')
                    lm = 15
            except Exception:
                messages.warning(request, 'Invalid lockout minutes; using default 15')
                lm = 15

            SystemSettings.objects.update_or_create(
                key='login_lockout_threshold', defaults={'value': str(lt), 'description': 'Failed login attempts threshold'}
            )
            SystemSettings.objects.update_or_create(
                key='login_lockout_minutes', defaults={'value': str(lm), 'description': 'Lockout duration in minutes'}
            )
            messages.success(request, 'Security settings saved')
            return redirect('admin_system_settings')

        else:
            # Fallback - single key save (keeps backward compatibility)
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

    settings_qs = SystemSettings.objects.all()
    # map for easy lookup in template
    settings_map = {s.key: s.value for s in settings_qs}
    context = {
        'settings': settings_qs,
        'settings_map': settings_map,
    }
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
def ADMIN_CALENDAR(request):
    """Simple calendar widget for admin"""
    from datetime import date
    from calendar import monthrange
    
    # Get current month/year or from request
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Get public holidays for the month
    public_holidays = PublicHoliday.objects.filter(
        date__year=year,
        date__month=month,
        is_active=True
    )
    
    # Get calendar events for the month (all active events created by admins)
    calendar_events = CalendarEvent.objects.filter(
        event_date__year=year,
        event_date__month=month,
        is_active=True
    ).order_by('event_date', 'start_time')
    
    # Build simple calendar widget data
    first_weekday = date(year, month, 1).weekday()  # Monday=0
    days_in_month = monthrange(year, month)[1]
    
    # Map holidays by date
    holiday_by_date = {h.date: h for h in public_holidays}
    
    # Map events by date
    events_by_date = {}
    for event in calendar_events:
        if event.event_date not in events_by_date:
            events_by_date[event.event_date] = []
        events_by_date[event.event_date].append(event)
    
    # Build simple calendar days
    calendar_days = []
    today = date.today()
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        calendar_days.append({
            'day': day,
            'date': current_date,
            'is_today': current_date == today,
            'holiday': holiday_by_date.get(current_date),
            'events': events_by_date.get(current_date, []),
        })
    
    context = {
        'current_year': year,
        'current_month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'leading_blanks': range(first_weekday),
        'calendar_days': calendar_days,
        'public_holidays': public_holidays,
        'calendar_events': calendar_events,
    }
    return render(request, 'admin/calendar.html', context)


@login_required(login_url='/')
@admin_required
def MANAGE_HOLIDAYS(request):
    """Manage public holidays"""
    from datetime import date
    
    if request.method == "POST":
        name = request.POST.get('name')
        holiday_date = request.POST.get('date')
        description = request.POST.get('description', '')
        is_recurring = request.POST.get('is_recurring') == 'on'
        
        if PublicHoliday.objects.filter(name=name, date=holiday_date).exists():
            messages.warning(request, 'This holiday already exists')
        else:
            PublicHoliday.objects.create(
                name=name,
                date=holiday_date,
                description=description,
                is_recurring=is_recurring
            )
            messages.success(request, 'Public holiday added successfully')
        
        return redirect('admin_manage_holidays')
    
    current_year = date.today().year
    holidays = PublicHoliday.objects.all().order_by('date')
    
    # Statistics
    total_holidays = holidays.count()
    upcoming_holidays = holidays.filter(date__gte=date.today()).count()
    recurring_holidays = holidays.filter(is_recurring=True).count()
    
    context = {
        'holidays': holidays,
        'current_year': current_year,
        'total_holidays': total_holidays,
        'upcoming_holidays': upcoming_holidays,
        'recurring_holidays': recurring_holidays,
    }
    return render(request, 'admin/manage_holidays.html', context)


@login_required(login_url='/')
@admin_required
def UPDATE_HOLIDAY(request, id):
    """Update public holiday"""
    holiday = get_object_or_404(PublicHoliday, id=id)
    
    if request.method == "POST":
        holiday.name = request.POST.get('name')
        holiday.date = request.POST.get('date')
        holiday.description = request.POST.get('description', '')
        holiday.is_recurring = request.POST.get('is_recurring') == 'on'
        holiday.is_active = request.POST.get('is_active') == 'on'
        holiday.save()
        messages.success(request, 'Holiday updated successfully')
        return redirect('admin_manage_holidays')
    
    context = {'holiday': holiday}
    return render(request, 'admin/update_holiday.html', context)


@login_required(login_url='/')
@admin_required
def DELETE_HOLIDAY(request, id):
    """Delete public holiday"""
    if request.method == 'POST':
        holiday = get_object_or_404(PublicHoliday, id=id)
        holiday.delete()
        messages.success(request, 'Holiday deleted successfully')
    return redirect('admin_manage_holidays')


@login_required(login_url='/')
@admin_required
def MANAGE_EVENTS(request):
    """Manage calendar events"""
    from datetime import date
    
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        event_date = request.POST.get('event_date')
        event_type = request.POST.get('event_type', 'other')
        location = request.POST.get('location', '')
        is_all_day = request.POST.get('is_all_day') == 'on'
        start_time = request.POST.get('start_time') or None
        end_time = request.POST.get('end_time') or None
        
        CalendarEvent.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            event_type=event_type,
            location=location,
            is_all_day=is_all_day,
            start_time=start_time,
            end_time=end_time,
            created_by=request.user
        )
        messages.success(request, 'Calendar event added successfully')
        return redirect('admin_manage_events')
    
    current_year = date.today().year
    events = CalendarEvent.objects.all().order_by('event_date', 'start_time')
    
    # Statistics
    total_events = events.count()
    upcoming_events = events.filter(event_date__gte=date.today()).count()
    
    context = {
        'events': events,
        'current_year': current_year,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'admin/manage_events.html', context)


@login_required(login_url='/')
@admin_required
def UPDATE_EVENT(request, id):
    """Update calendar event"""
    event = get_object_or_404(CalendarEvent, id=id)
    
    if request.method == "POST":
        event.title = request.POST.get('title')
        event.description = request.POST.get('description', '')
        event.event_date = request.POST.get('event_date')
        event.event_type = request.POST.get('event_type', 'other')
        event.location = request.POST.get('location', '')
        event.is_all_day = request.POST.get('is_all_day') == 'on'
        event.is_active = request.POST.get('is_active') == 'on'
        event.start_time = request.POST.get('start_time') or None
        event.end_time = request.POST.get('end_time') or None
        event.save()
        messages.success(request, 'Event updated successfully')
        return redirect('admin_manage_events')
    
    context = {'event': event}
    return render(request, 'admin/update_event.html', context)


@login_required(login_url='/')
@admin_required
def DELETE_EVENT(request, id):
    """Delete calendar event"""
    if request.method == 'POST':
        event = get_object_or_404(CalendarEvent, id=id)
        event.delete()
        messages.success(request, 'Event deleted successfully')
    return redirect('admin_manage_events')
