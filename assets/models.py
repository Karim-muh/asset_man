from django.db import models
from django.conf import settings

# Create your models here.


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('USER', 'Ordinary User'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Administrator'),
    ]

    STAFF_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='USER'
    )

    staff_status = models.CharField(
        max_length=20,
        choices=STAFF_STATUS_CHOICES,
        default='PENDING'
    )

    # Retained temporarily for compatibility with your existing database.
    # Staff authorization will use staff_status and role instead.
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"



class Department(models.Model):
    department_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    employee_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    job_title = models.CharField(max_length=100)
    department = models.ForeignKey(Department,on_delete=models.PROTECT,related_name='employees')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Asset(models.Model):

    CATEGORY_CHOICES = [
        ('Computer', 'Computer'),
        ('Furniture', 'Furniture'),
        ('Vehicle', 'Vehicle'),
        ('Equipment', 'Equipment'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Disposed', 'Disposed'),
    ]

    asset_tag = models.CharField(max_length=30, unique=True)
    asset_name = models.CharField(max_length=150)
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True)
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=12,decimal_places=2)
    department = models.ForeignKey(Department,on_delete=models.PROTECT,related_name='assets')
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset_tag} - {self.asset_name}"


class Requisition(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Fulfilled', 'Fulfilled'),
    ]

    requisition_number = models.CharField(max_length=30, unique=True)
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name='requisitions')
    asset_category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    date_requested = models.DateField()
    purpose = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')

    def __str__(self):
        return self.requisition_number


class Distribution(models.Model):
    asset = models.ForeignKey(Asset,on_delete=models.PROTECT,related_name='distributions')
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name='distributions')
    date_issued = models.DateField()
    expected_return_date = models.DateField(null=True,blank=True)
    actual_return_date = models.DateField(null=True,blank=True)
    condition_on_issue = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset} - {self.employee}"


class Disposal(models.Model):

    METHOD_CHOICES = [
        ('Sale', 'Sale'),
        ('Donation', 'Donation'),
        ('Recycling', 'Recycling'),
        ('Destruction', 'Destruction'),
    ]

    asset = models.OneToOneField(Asset,on_delete=models.PROTECT,related_name='disposal')
    date_disposed = models.DateField()
    reason = models.TextField()
    method = models.CharField(max_length=30,choices=METHOD_CHOICES)
    approved_by = models.ForeignKey(Employee,on_delete=models.PROTECT)
    disposal_value = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Disposal - {self.asset}"
