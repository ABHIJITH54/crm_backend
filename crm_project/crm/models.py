
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone


def today_date():
  
    return timezone.localdate()


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # created once
    updated_at = models.DateTimeField(auto_now=True)      # updated automatically

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        fn = (self.first_name or '').strip()
        ln = (self.last_name or '').strip()
        full = (fn + ' ' + ln).strip() or self.username or self.email
        return f"{full} ({self.email})"


from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=[('active', 'Active'), ('inactive', 'Inactive')], 
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name



from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='manager_profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='managers')
    team_name = models.CharField(max_length=100, blank=True, null=True)  # Changed from 'team' to 'team_name'
    status = models.CharField(
        max_length=20, 
        choices=[('active', 'Active'), ('inactive', 'Inactive')], 
        default='active'
    )
    joined_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"



from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    skill = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=[('active', 'Active'), ('inactive', 'Inactive')], 
        default='active'
    )
    joined_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"



class Customer(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),  
        ('Converted', 'Converted'),
    ]

    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='customers/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    added_date = models.DateField(default=today_date)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_customer = Customer.objects.select_for_update().order_by('id').last()
            if last_customer and last_customer.customer_id.startswith('CS'):
                try:
                    last_number = int(last_customer.customer_id[2:])
                    new_number = last_number + 1
                except (ValueError, TypeError):
                    new_number = Customer.objects.count() + 1
            else:
                new_number = Customer.objects.count() + 1
            
            self.customer_id = f"CS{new_number:03d}"
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.customer_id})"
