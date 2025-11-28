
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .import views, staffviews, adminviews, departmentheadviews, hrviews, superadminviews
from .password_reset_views import CustomPasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', views.BASE, name='base'),
    #login Path
    path('', views.FIRSTPAGE, name='firstpage'),
    path('Login', views.LOGIN, name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('doLogout', views.doLogout, name='logout'),

    path('Index', views.INDEX, name='index'),
    
    # Legacy Admin Panel (for backward compatibility)
    path('Admin/Home', adminviews.HOME, name='admin_home'),
    path('Admin/Staff/Add',adminviews.ADD_STAFF,name='add_staff'),
    path('Admin/Staff/View',adminviews.VIEW_STAFF,name='view_staff'),
    path('Admin/Staff/Edit/<str:id>',adminviews.EDIT_STAFF,name='edit_staff'),
    path('Admin/Staff/Update',adminviews.UPDATE_STAFF,name='update_staff'),
    path('Admin/Staff/<str:admin>',adminviews.DELETE_STAFF,name='delete_staff'),
    path('Admin/Leaveview',adminviews.STAFF_LEAVE_VIEW,name='staff_leave_view_admin'),
    path('Admin/Staff/Approve_Leave/<str:id>',adminviews.STAFF_APPROVE_LEAVE,name='staff_approve_leave'),
    path('Admin/Staff/Disapprove_Leave/<str:id>',adminviews.STAFF_DISAPPROVE_LEAVE,name='staff_disapprove_leave'),

    # Admin Panel (includes all super admin functionality)
    path('Admin/Users', adminviews.MANAGE_USERS, name='admin_manage_users'),
    path('Admin/Users/Create', adminviews.CREATE_USER, name='admin_create_user'),
    path('Admin/Users/Edit/<str:id>', adminviews.EDIT_USER, name='admin_edit_user'),
    path('Admin/Users/Deactivate/<str:id>', adminviews.DEACTIVATE_USER, name='admin_deactivate_user'),
    path('Admin/Users/Activate/<str:id>', adminviews.ACTIVATE_USER, name='admin_activate_user'),
    path('Admin/Users/Delete/<str:id>', adminviews.DELETE_USER, name='admin_delete_user'),
    path('Admin/Roles/Assign', adminviews.ASSIGN_ROLES, name='admin_assign_roles'),
    path('Admin/Departments', adminviews.MANAGE_DEPARTMENTS, name='admin_manage_departments'),
    path('Admin/Departments/Update/<str:id>', adminviews.UPDATE_DEPARTMENT, name='admin_update_department'),
    path('Admin/Departments/Delete/<str:id>', adminviews.DELETE_DEPARTMENT, name='admin_delete_department'),
    path('Admin/Settings', adminviews.SYSTEM_SETTINGS, name='admin_system_settings'),
    path('Admin/Settings/Update/<str:id>', adminviews.UPDATE_SETTING, name='admin_update_setting'),
    path('Admin/Auth/Config', adminviews.AUTH_CONFIGURATION, name='admin_auth_config'),
    
    # Legacy Super Admin routes (redirect to admin routes for backward compatibility)
    path('SuperAdmin/Home', adminviews.HOME, name='superadmin_home'),
    path('SuperAdmin/Users', adminviews.MANAGE_USERS, name='superadmin_manage_users'),
    path('SuperAdmin/Users/Create', adminviews.CREATE_USER, name='superadmin_create_user'),
    path('SuperAdmin/Users/Edit/<str:id>', adminviews.EDIT_USER, name='superadmin_edit_user'),
    path('SuperAdmin/Users/Deactivate/<str:id>', adminviews.DEACTIVATE_USER, name='superadmin_deactivate_user'),
    path('SuperAdmin/Users/Activate/<str:id>', adminviews.ACTIVATE_USER, name='superadmin_activate_user'),
    path('SuperAdmin/Users/Delete/<str:id>', adminviews.DELETE_USER, name='superadmin_delete_user'),
    path('SuperAdmin/Roles/Assign', adminviews.ASSIGN_ROLES, name='superadmin_assign_roles'),
    path('SuperAdmin/Departments', adminviews.MANAGE_DEPARTMENTS, name='superadmin_manage_departments'),
    path('SuperAdmin/Departments/Update/<str:id>', adminviews.UPDATE_DEPARTMENT, name='superadmin_update_department'),
    path('SuperAdmin/Departments/Delete/<str:id>', adminviews.DELETE_DEPARTMENT, name='superadmin_delete_department'),
    path('SuperAdmin/Settings', adminviews.SYSTEM_SETTINGS, name='superadmin_system_settings'),
    path('SuperAdmin/Settings/Update/<str:id>', adminviews.UPDATE_SETTING, name='superadmin_update_setting'),
    path('SuperAdmin/Auth/Config', adminviews.AUTH_CONFIGURATION, name='superadmin_auth_config'),

    # Department Head Panel
    path('DepartmentHead/Home', departmentheadviews.HOME, name='dh_home'),
    path('DepartmentHead/Review/Leaves', departmentheadviews.REVIEW_LEAVE_APPLICATIONS, name='dh_review_leaves'),
    path('DepartmentHead/Approve/<str:id>', departmentheadviews.APPROVE_LEAVE, name='dh_approve_leave'),
    path('DepartmentHead/Reject/<str:id>', departmentheadviews.REJECT_LEAVE, name='dh_reject_leave'),
    path('DepartmentHead/Calendar', departmentheadviews.DEPARTMENTAL_CALENDAR, name='dh_calendar'),
    path('DepartmentHead/Team/Schedules', departmentheadviews.MANAGE_TEAM_SCHEDULES, name='dh_team_schedules'),

    # HR Panel
    path('HR/Home', hrviews.HOME, name='hr_home'),
    path('HR/Staff/Manage', hrviews.MANAGE_STAFF, name='hr_manage_staff'),
    path('HR/Staff/Add', hrviews.ADD_STAFF, name='hr_add_staff'),
    path('HR/Staff/Update/<str:id>', hrviews.UPDATE_STAFF, name='hr_update_staff'),
    path('HR/LeaveTypes/Manage', hrviews.MANAGE_LEAVE_TYPES, name='hr_manage_leave_types'),
    path('HR/LeaveTypes/Update/<str:id>', hrviews.UPDATE_LEAVE_TYPE, name='hr_update_leave_type'),
    path('HR/Entitlements/Set', hrviews.SET_LEAVE_ENTITLEMENTS, name='hr_set_entitlements'),
    path('HR/Entitlements/Delete/<str:id>', hrviews.DELETE_ENTITLEMENT, name='hr_delete_entitlement'),
    path('HR/Leave/Approve', hrviews.APPROVE_OVERRIDE_LEAVE, name='hr_approve_leave'),
    path('HR/Leave/Approve/<str:id>', hrviews.HR_APPROVE_LEAVE, name='hr_approve_leave_action'),
    path('HR/Leave/Reject/<str:id>', hrviews.HR_REJECT_LEAVE, name='hr_reject_leave'),
    path('HR/Reports', hrviews.GENERATE_REPORTS, name='hr_reports'),
    path('HR/Reports/Export', hrviews.EXPORT_REPORT, name='hr_export_report'),
    path('HR/Holidays/Manage', hrviews.MANAGE_PUBLIC_HOLIDAYS, name='hr_manage_holidays'),
    path('HR/Holidays/Update/<str:id>', hrviews.UPDATE_HOLIDAY, name='hr_update_holiday'),
    path('HR/Holidays/Delete/<str:id>', hrviews.DELETE_HOLIDAY, name='hr_delete_holiday'),

    # Staff Panel
    path('Staff/Home', staffviews.HOME, name='staff_home'),
    path('Staff/Apply_Leave', staffviews.STAFF_APPLY_LEAVE, name='staff_apply_leave'),
    path('Staff/Apply_Leave_save', staffviews.STAFF_APPLY_LEAVE_SAVE, name='staff_apply_leave_save'),
    path('Staff/Leaveview', staffviews.STAFF_LEAVE_VIEW, name='staff_leave_view'),
    path('Staff/Leave/Balance', staffviews.VIEW_LEAVE_BALANCE, name='staff_leave_balance'),
    path('Staff/Leave/Track/<str:leave_id>', staffviews.TRACK_LEAVE_STATUS, name='staff_track_leave'),
    
    #profile path
    path('Profile', views.PROFILE, name='profile'),
    path('Profile/update', views.PROFILE_UPDATE, name='profile_update'),
    path('Password', views.CHANGE_PASSWORD, name='change_password'),

    # Password Reset URLs
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),



] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
