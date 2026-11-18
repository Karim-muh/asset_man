# Create your views here.
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import UserProfile,Asset, Requisition, Distribution, Disposal, Department, Employee
from .forms import LoginForm, RegistrationForm, UserProfileForm, AssetForm, RequisitionForm, DistributionForm, DisposalForm, DepartmentForm, EmployeeForm, EmployeeCreateForm

def is_admin_user(user):
    """Check whether the user is an administrator."""
    if user.is_superuser or user.is_staff:
        return True

    profile = UserProfile.objects.filter(user=user).first()

    return bool(profile and profile.role == 'ADMIN' and profile.is_approved)


def is_approved_user(user):
    """Check whether the user has an approved account in any supported role."""
    if user.is_superuser or user.is_staff:
        return True

    profile = UserProfile.objects.filter(user=user).first()

    return bool(
        profile
        and (profile.is_approved or profile.staff_status == 'APPROVED')
        and profile.role in ['USER', 'STAFF', 'ADMIN']
    )


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request,username=username,password=password)
            if user is not None:
                if is_approved_user(user):
                    login(request, user)

                    messages.success(request,f'Welcome back, {user.username}!')

                    return redirect('dashboard')

                else:
                    messages.error(request,'Your account is awaiting administrator approval or has no approved user profile.')
            else:
                messages.error(request,'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request,'assets/login.html',{'form': form})

@login_required(login_url='login')
def user_logout(request):
    logout(request)

    messages.success(
        request,
        'You have logged out successfully.'
    )

    return redirect('login')


def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.create(
                    user=user,
                    role='USER',
                    is_approved=False,
                    staff_status='PENDING',
                )
            messages.success(
                request,
                'Your user account was created and is awaiting administrator approval. It has not been added as an employee.',
            )
            return redirect('login')
        messages.error(request, 'Please correct the errors in the registration form.')
    else:
        form = RegistrationForm()

    return render(request, 'assets/register.html', {'form': form})



@login_required(login_url='login')
def dashboard(request):

    # Check account approval
    # Check account approval
    if not is_approved_user(request.user):
        logout(request)
        messages.error(request,'Your account has not been approved or user profile not found.')
        return redirect('login')
        

    # Retrieve dashboard statistics from the database
    total_assets = Asset.objects.count()

    available_assets = Asset.objects.filter(status='Available').count()

    assigned_assets = Asset.objects.filter(status='Assigned').count()

    total_employees = Employee.objects.count()

    # Retrieve the latest acquired assets
    recent_assets = Asset.objects.select_related('department').order_by('-acquisition_date')[:5]

    context = {
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'total_employees': total_employees,
        'recent_assets': recent_assets,
        'can_delete_records': is_admin_user(request.user),
    }

    return render(request,'assets/dashboard.html',context)


@login_required(login_url='login')
def user_list(request):

    # Only administrators can manage users
   # Only administrators can manage users
    if not is_admin_user(request.user):
        messages.error(request,'You do not have permission to manage users.')
        return redirect('dashboard')

    # Get all Django user accounts
    User = get_user_model()
    all_users = User.objects.all()

    # Create profiles for accounts that do not have one
    for user in all_users:

        profile = UserProfile.objects.filter(user=user).first()

        if profile is None:

            if user.is_staff or user.is_superuser:
                role = 'ADMIN'
                approved = True
            else:
                role = 'STAFF'
                approved = False

            UserProfile.objects.create(user=user,role=role,is_approved=approved)

    # Retrieve all user profiles
    users = UserProfile.objects.select_related('user').order_by('-created_at')

    context = {
        'users': users,
        'current_user_id': request.user.id,
        }

    return render(request,'assets/user_list.html',context)

@login_required(login_url='login')
def user_edit(request, profile_id):

    # Only administrators can edit users
    if not is_admin_user(request.user):
        messages.error( request,'You do not have permission to edit users.')
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile,id=profile_id)

    if request.method == 'POST':

        form = UserProfileForm(request.POST,instance=profile)

        if form.is_valid():

            profile = form.save()
            profile.staff_status = 'APPROVED' if profile.is_approved else 'PENDING'
            profile.save(update_fields=['staff_status'])

            messages.success(request,'User profile updated successfully.')

            return redirect('user_list')

        else:
            messages.error(request,'Please correct the errors in the form.')

    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(request,'assets/user_edit.html',context)


@login_required(login_url='login')
def user_delete(request, profile_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete user accounts.')
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile,id=profile_id)

    if request.method == 'POST':

        username = profile.user.username

        # Delete the user and associated profile
        profile.user.delete()

        messages.success(request,f'User account {username} deleted successfully.')

        return redirect('user_list')

    return render(request,'assets/user_delete.html',{'profile': profile})


@login_required(login_url='login')
def department_list(request):

    # Approved users can view and maintain department records.
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    # Retrieve departments from the database
    departments = Department.objects.all().order_by('name')

    context = {
        'departments': departments,
        'can_delete_records': is_admin_user(request.user),
    }

    return render(request,'assets/department_list.html',context)

@login_required(login_url='login')
def department_create(request):

    if not is_approved_user(request.user):
        messages.error(request,'Your account must be approved to register departments.')
        return redirect('dashboard')

    if request.method == 'POST':

        form = DepartmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request,'Department registered successfully.')

            return redirect('department_list')

        else:
            messages.error(request,'Please correct the errors in the department form.')

    else:
        form = DepartmentForm()

    context = {
        'form': form,
        'page_title': 'Register Department',
    }

    return render(request,'assets/department_form.html',context)

@login_required(login_url='login')
def department_edit(request, department_id):

    if not is_approved_user(request.user):
        messages.error(request,'Your account must be approved to edit departments.')
        return redirect('dashboard')

    department = get_object_or_404(Department,id=department_id)

    if request.method == 'POST':

        form = DepartmentForm(request.POST,instance=department)

        if form.is_valid():

            form.save()

            messages.success(request,'Department details updated successfully.')

            return redirect('department_list')

        else:
            messages.error(request,'Please correct the errors in the department form.')

    else:
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
        'page_title': 'Edit Department',
    }

    return render(request,'assets/department_form.html',context)

@login_required(login_url='login')
def department_delete(request, department_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete departments.')
        return redirect('department_list')

    department = get_object_or_404(Department,id=department_id)

    if request.method == 'POST':

        department_name = department.name

        department.delete()

        messages.success( request,f'Department {department_name} deleted successfully.')

        return redirect('department_list')

    # Display the confirmation page without deleting anything
    return render(request,'assets/department_delete.html',{'department': department})

@login_required(login_url='login')
def employee_list(request):

    # Approved users can view employee records; registration stays administrator-only.
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    # Retrieve employees and their departments
    employees = Employee.objects.select_related('department', 'user').all().order_by('first_name')

    context = {
        'employees': employees,
        'can_manage_employees': is_admin_user(request.user),
        'can_edit_employees': is_approved_user(request.user),
        'can_delete_records': is_admin_user(request.user),
    }

    return render(request,'assets/employee_list.html',context)

@login_required(login_url='login')
def employee_create(request):

    # Only administrators can register employees
    if not is_admin_user(request.user):
        messages.error(request,'You do not have permission to register employees.')
        return redirect('dashboard')

    if request.method == 'POST':

        form = EmployeeCreateForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = get_user_model().objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password=form.cleaned_data['password1'],
                )
                UserProfile.objects.create(
                    user=user,
                    role='STAFF',
                    is_approved=True,
                    staff_status='APPROVED',
                )
                employee = form.save(commit=False)
                employee.user = user
                employee.save()

            messages.success(request,'Employee and login account created successfully.')

            return redirect('employee_list')

        else:
            messages.error(request,'Please correct the errors in the employee form.')

    else:
        form = EmployeeCreateForm()

    context = {
        'form': form,
        'page_title': 'Register Employee',
    }

    return render(request,'assets/employee_form.html',context)

@login_required(login_url='login')
def employee_edit(request, employee_id):

    if not is_approved_user(request.user):
        messages.error(request,'Your account must be approved to edit employees.')
        return redirect('dashboard')

    employee = get_object_or_404(Employee,id=employee_id)

    if request.method == 'POST':

        form = EmployeeForm(request.POST,instance=employee)

        if form.is_valid():

            employee = form.save()
            if employee.user:
                employee.user.first_name = employee.first_name
                employee.user.last_name = employee.last_name
                employee.user.email = employee.email
                employee.user.save(update_fields=['first_name', 'last_name', 'email'])

            messages.success(request,'Employee details updated successfully.')

            return redirect('employee_list')

        else:
            messages.error(request,'Please correct the errors in the employee form.')

    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'page_title': 'Edit Employee',
    }

    return render(request,'assets/employee_form.html',context)


@login_required(login_url='login')
def employee_delete(request, employee_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete employees.')
        return redirect('employee_list')

    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':

        employee_name = f'{employee.first_name} {employee.last_name}'

        employee.delete()

        messages.success(
            request,
            f'Employee {employee_name} deleted successfully.'
        )

        return redirect('employee_list')

    return render(
        request,
        'assets/employee_delete.html',
        {'employee': employee}
    )

@login_required(login_url='login')
def asset_list(request):

    # Approved users can view and maintain asset records.
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    # Retrieve assets and their departments
    assets = Asset.objects.select_related('department').all().order_by('asset_name')

    context = {
        'assets': assets,
        'can_delete_records': is_admin_user(request.user),
    }

    return render(request,'assets/asset_list.html',context)

@login_required(login_url='login')
def asset_create(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to register assets.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AssetForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Asset registered successfully.')
            return redirect('asset_list')
        else:
            messages.error(request, 'Please correct the errors in the asset form.')

    else:
        form = AssetForm()

    context = {
        'form': form,
        'page_title': 'Register Asset'
    }

    return render(request, 'assets/asset_form.html', context)


@login_required(login_url='login')
def asset_edit(request, asset_id):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to edit assets.')
        return redirect('dashboard')

    asset = get_object_or_404(Asset, id=asset_id)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)

        if form.is_valid():
            form.save()
            messages.success(request, 'Asset details updated successfully.')
            return redirect('asset_list')
        else:
            messages.error(request, 'Please correct the errors in the asset form.')

    else:
        form = AssetForm(instance=asset)

    context = {
        'form': form,
        'asset': asset,
        'page_title': 'Edit Asset'
    }

    return render(request, 'assets/asset_form.html', context)


@login_required(login_url='login')
def asset_delete(request, asset_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete assets.')
        return redirect('asset_list')

    asset = get_object_or_404(Asset, id=asset_id)

    if request.method == 'POST':

        asset_name = asset.asset_name
        asset.delete()

        messages.success(request,f'Asset {asset_name} deleted successfully.')

        return redirect('asset_list')

    return render(request,'assets/asset_delete.html',{'asset': asset})


@login_required(login_url='login')
def requisition_list(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    requisitions = Requisition.objects.select_related('employee').all().order_by('-date_requested')

    return render(request,'assets/requisition_list.html',{
        'requisitions': requisitions,
        'can_delete_records': is_admin_user(request.user),
    })


@login_required(login_url='login')
def requisition_create(request):
    if not is_approved_user(request.user):
        messages.error(request, 'You do not have permission to create requisitions.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = RequisitionForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Requisition created successfully.')
            return redirect('requisition_list')
        else:
            messages.error(request, 'Please correct the errors in the requisition form.')
    else:
        form = RequisitionForm()

    context = {
        'form': form,
        'page_title': 'Create Requisition'
    }

    return render(request, 'assets/requisition_form.html', context)


@login_required(login_url='login')
def requisition_edit(request, requisition_id):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to edit requisitions.')
        return redirect('dashboard')

    requisition = get_object_or_404(Requisition, id=requisition_id)

    if request.method == 'POST':
        form = RequisitionForm(request.POST, instance=requisition)

        if form.is_valid():
            form.save()
            messages.success(request, 'Requisition updated successfully.')
            return redirect('requisition_list')
        else:
            messages.error(request, 'Please correct the errors in the requisition form.')
    else:
        form = RequisitionForm(instance=requisition)

    context = {
        'form': form,
        'requisition': requisition,
        'page_title': 'Edit Requisition'
    }

    return render(request, 'assets/requisition_form.html', context)


@login_required(login_url='login')
def requisition_delete(request, requisition_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete requisitions.')
        return redirect('requisition_list')

    requisition = get_object_or_404(Requisition, id=requisition_id)

    if request.method == 'POST':
        requisition_number = requisition.requisition_number
        requisition.delete()

        messages.success(request,f'Requisition {requisition_number} deleted successfully.')

        return redirect('requisition_list')

    return render(request,'assets/requisition_delete.html',{'requisition': requisition})


@login_required(login_url='login')
def distribution_list(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    distributions = Distribution.objects.select_related('asset','employee').all().order_by('-date_issued')

    return render(request,'assets/distribution_list.html',{
        'distributions': distributions,
        'can_delete_records': is_admin_user(request.user),
    })


@login_required(login_url='login')
def distribution_create(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to issue assets.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = DistributionForm(request.POST)

        if form.is_valid():
            distribution = form.save()

            # Update the asset status when it is issued
            asset = distribution.asset
            asset.status = 'Assigned'
            asset.save(update_fields=['status'])

            messages.success(request, 'Asset issued to employee successfully.')
            return redirect('distribution_list')

        else:
            messages.error(request, 'Please correct the errors in the distribution form.')

    else:
        form = DistributionForm()

    context = {
        'form': form,
        'page_title': 'Issue Asset'
    }

    return render(request, 'assets/distribution_form.html', context)


@login_required(login_url='login')
def distribution_edit(request, distribution_id):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to edit distributions.')
        return redirect('dashboard')

    distribution = get_object_or_404(Distribution, id=distribution_id)

    if request.method == 'POST':
        form = DistributionForm(request.POST, instance=distribution)

        if form.is_valid():
            form.save()
            messages.success(request, 'Distribution details updated successfully.')
            return redirect('distribution_list')

        else:
            messages.error(request, 'Please correct the errors in the distribution form.')

    else:
        form = DistributionForm(instance=distribution)

    context = {
        'form': form,
        'distribution': distribution,
        'page_title': 'Edit Distribution'
    }

    return render(request, 'assets/distribution_form.html', context)


@login_required(login_url='login')
def distribution_delete(request, distribution_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete distributions.')
        return redirect('distribution_list')

    distribution = get_object_or_404(Distribution,id=distribution_id)

    if request.method == 'POST':

        asset = distribution.asset

        distribution.delete()

        # Restore the asset status
        if not asset.distributions.filter(actual_return_date__isnull=True).exists():
            asset.status = 'Available'
            asset.save(update_fields=['status'])

        messages.success(request,'Distribution record deleted successfully.')

        return redirect('distribution_list')

    return render(request,'assets/distribution_delete.html',{'distribution': distribution})


@login_required(login_url='login')
def distribution_list(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    distributions = Distribution.objects.select_related('asset','employee').all().order_by('-date_issued')
    return render(request,'assets/distribution_list.html',{
        'distributions': distributions,
        'can_delete_records': is_admin_user(request.user),
    })


@login_required(login_url='login')
def distribution_create(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to issue assets.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = DistributionForm(request.POST)

        if form.is_valid():
            distribution = form.save()

            # Update the asset status when it is issued
            asset = distribution.asset
            asset.status = 'Assigned'
            asset.save(update_fields=['status'])

            messages.success(request, 'Asset issued to employee successfully.')
            return redirect('distribution_list')

        else:
            messages.error(request, 'Please correct the errors in the distribution form.')

    else:
        form = DistributionForm()

    context = {
        'form': form,
        'page_title': 'Issue Asset'
    }

    return render(request, 'assets/distribution_form.html', context)


@login_required(login_url='login')
def distribution_edit(request, distribution_id):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to edit distributions.')
        return redirect('dashboard')

    distribution = get_object_or_404(Distribution, id=distribution_id)

    if request.method == 'POST':
        form = DistributionForm(request.POST, instance=distribution)

        if form.is_valid():
            form.save()
            messages.success(request, 'Distribution details updated successfully.')
            return redirect('distribution_list')

        else:
            messages.error(request, 'Please correct the errors in the distribution form.')

    else:
        form = DistributionForm(instance=distribution)

    context = {
        'form': form,
        'distribution': distribution,
        'page_title': 'Edit Distribution'
    }

    return render(request, 'assets/distribution_form.html', context)


@login_required(login_url='login')
def distribution_delete(request, distribution_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete distributions.')
        return redirect('distribution_list')

    distribution = get_object_or_404(Distribution,id=distribution_id)

    if request.method == 'POST':

        asset = distribution.asset

        distribution.delete()

        # Restore the asset status
        if not asset.distributions.filter(actual_return_date__isnull=True).exists():
            asset.status = 'Available'
            asset.save(update_fields=['status'])

        messages.success(request,'Distribution record deleted successfully.')

        return redirect('distribution_list')

    return render(request,'assets/distribution_delete.html',{'distribution': distribution})


@login_required(login_url='login')
def disposal_list(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account is not approved.')
        return redirect('login')

    disposals = Disposal.objects.select_related('asset','approved_by').all().order_by('-date_disposed')

    return render(request,'assets/disposal_list.html',{
        'disposals': disposals,
        'can_delete_records': is_admin_user(request.user),
    })


@login_required(login_url='login')
def disposal_create(request):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to register disposals.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = DisposalForm(request.POST)

        if form.is_valid():
            disposal = form.save()

            # Update the asset status after disposal
            asset = disposal.asset
            asset.status = 'Disposed'
            asset.save(update_fields=['status'])

            messages.success(request, 'Asset disposal recorded successfully.')
            return redirect('disposal_list')

        else:
            messages.error(request, 'Please correct the errors in the disposal form.')

    else:
        form = DisposalForm()

    context = {
        'form': form,
        'page_title': 'Register Asset Disposal'
    }

    return render(request, 'assets/disposal_form.html', context)


@login_required(login_url='login')
def disposal_edit(request, disposal_id):
    if not is_approved_user(request.user):
        messages.error(request, 'Your account must be approved to edit disposals.')
        return redirect('dashboard')

    disposal = get_object_or_404(Disposal, id=disposal_id)

    if request.method == 'POST':
        form = DisposalForm(request.POST, instance=disposal)

        if form.is_valid():
            form.save()

            # Keep the asset status as disposed
            asset = disposal.asset
            asset.status = 'Disposed'
            asset.save(update_fields=['status'])

            messages.success(request, 'Disposal details updated successfully.')
            return redirect('disposal_list')

        else:
            messages.error(request, 'Please correct the errors in the disposal form.')

    else:
        form = DisposalForm(instance=disposal)

    context = {
        'form': form,
        'disposal': disposal,
        'page_title': 'Edit Disposal'
    }

    return render(request, 'assets/disposal_form.html', context)


@login_required(login_url='login')
def disposal_delete(request, disposal_id):
    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can delete disposals.')
        return redirect('disposal_list')

    disposal = get_object_or_404(Disposal, id=disposal_id)

    if request.method == 'POST':

        asset = disposal.asset

        disposal.delete()

        # Restore the asset status after removing its disposal record
        asset.status = 'Available'
        asset.save(update_fields=['status'])

        messages.success(request, 'Disposal record deleted successfully.')
        return redirect('disposal_list')

    return render(request,'assets/disposal_delete.html',{'disposal': disposal})




@login_required(login_url='login')
def report_list(request):

    if not is_admin_user(request.user):
        messages.error(request, 'Only administrators can access reports.')
        return redirect('dashboard')

    # Retrieve filter values
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    department = request.GET.get('department', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Retrieve all assets with their departments
    assets = Asset.objects.select_related('department').all()

    # Filter by asset status
    if status:
        assets = assets.filter(status=status)

    # Filter by asset category
    if category:
        assets = assets.filter(category=category)

    # Filter by department
    if department:
        try:
            department_id = int(department)
            assets = assets.filter(department_id=department_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid department selection.')
            department = ''

    # Filter by acquisition date
    if start_date:
        assets = assets.filter(acquisition_date__gte=start_date)

    if end_date:
        assets = assets.filter(acquisition_date__lte=end_date)

    # Arrange assets by acquisition date
    assets = assets.order_by('-acquisition_date')

    # Prepare report information
    context = {

        # Compact summary figures
        'total_assets': Asset.objects.count(),
        'total_employees': Employee.objects.count(),
        'total_disposals': Disposal.objects.count(),

        # Filtered asset records
        'filtered_assets': assets,
        'filtered_count': assets.count(),

        # Filter options
        'status_choices': Asset.STATUS_CHOICES,
        'category_choices': Asset.CATEGORY_CHOICES,
        'departments': Department.objects.all().order_by('name'),

        # Preserve selected filters
        'selected_status': status,
        'selected_category': category,
        'selected_department': department,
        'start_date': start_date,
        'end_date': end_date,

        # Recent disposal records
        'recent_disposals': Disposal.objects.select_related('asset').order_by('-date_disposed')[:5],
    }

    return render(request,'assets/report_list.html',context)


@login_required(login_url='login')
def settings(request):

    if not is_admin_user(request.user):
        messages.error(request,'You do not have permission to access settings.')
        return redirect('dashboard')

    return render(request,'assets/settings.html')
