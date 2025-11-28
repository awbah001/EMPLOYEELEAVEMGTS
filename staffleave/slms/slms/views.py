from django.shortcuts import render,redirect,HttpResponse
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import  logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

def BASE(request):
    return render(request,'base.html')

def FIRSTPAGE(request):
    return redirect('login')

def LOGIN(request):
    return render(request,'login.html')

def doLogin(request):
    if request.method == 'POST':
        user = EmailBackEnd.authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )
        if user is not None:
            if not user.is_active:
                messages.error(request, 'This account is inactive. Please contact the administrator.')
                return redirect('login')
            login(request, user)
            user_type = user.user_type
            if user_type == '1':  # Super Admin
                return redirect('superadmin_home')
            elif user_type == '2':  # Staff
                return redirect('staff_home')
            elif user_type == '3':  # Department Head
                return redirect('dh_home')
            elif user_type == '4':  # HR
                return redirect('hr_home')
            else:
                messages.error(request, 'Account type not recognized.')
                return redirect('login')
        else:
            messages.error(request, 'Email or Password is not valid')
            return redirect('login')
    else:
        messages.error(request, 'Email or Password is not valid')
        return redirect('login')
        


def doLogout(request):
    logout(request)
    return redirect('login')
@login_required(login_url='/')
def INDEX(request):
     return render(request,'index.html')

@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    context = {
        "user":user,
    }
    return render(request,'profile.html',context)
@login_required(login_url = '/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        try:
            customuser = CustomUser.objects.get(id = request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if profile_pic !=None and profile_pic != "":
               customuser.profile_pic = profile_pic
            customuser.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, customuser)
            messages.success(request,"Your profile has been updated successfully")
            return redirect('profile')
        except Exception as e:
            print("Profile update error:", e)  # log the exception for debug
            messages.error(request,"Your profile updation has been failed")
    return render(request, 'profile.html')


@login_required(login_url='/')
def CHANGE_PASSWORD(request):
     context ={}
     ch = User.objects.filter(id = request.user.id)
     
     if len(ch)>0:
            data = User.objects.get(id = request.user.id)
            context["data"]:data            
     if request.method == "POST":        
        current = request.POST["cpwd"]
        new_pas = request.POST['npwd']
        user = User.objects.get(id = request.user.id)
        un = user.username
        check = user.check_password(current)
        if check == True:
          user.set_password(new_pas)
          user.save()
          messages.success(request,'Password Change  Succeesfully!!!')
          user = User.objects.get(username=un)
          login(request,user)
        else:
          messages.success(request,'Current Password wrong!!!')
          return redirect("change_password")
     return render(request,'change-password.html')