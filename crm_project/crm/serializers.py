
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Department, Manager, Staff, Customer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  
    username_field = 'email'

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError('Must include email and password')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        
        data = super().validate({'email': email, 'password': password, 'username': email})

   
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        }
        return data

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone', 'profile_picture', 'password', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user



class DepartmentSerializer(serializers.ModelSerializer):
    staff_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'status', 'staff_count', 'created_at', 'updated_at']
        read_only_fields = ['staff_count', 'created_at', 'updated_at']

    def get_staff_count(self, obj):
        """
        Safely count related staff/managers
        """
        try:
           
            if hasattr(obj, 'staff_set'):
                return obj.staff_set.count()
            elif hasattr(obj, 'manager_set'):
                return obj.manager_set.count()
            elif hasattr(obj, 'managers'):
                return obj.managers.count()
            else:
                return 0
        except Exception:
            return 0




from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class ManagerSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    staff_count = serializers.SerializerMethodField()

   
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    user_email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=False)  # Made optional

    class Meta:
        model = Manager
        fields = [
            'id', 'username', 'name', 'email',
            'department', 'department_name',
            'team_name', 'employee_id', 'phone', 'status', 'joined_date',
            'staff_count', 'created_at', 'updated_at',
            'first_name', 'last_name', 'user_email', 'password'
        ]
        read_only_fields = ['created_at', 'updated_at', 'staff_count', 'department_name', 'username', 'name', 'email', 'employee_id']

    def get_staff_count(self, obj):
       
        try:
            return obj.staff_members.count() if hasattr(obj, 'staff_members') else 0
        except AttributeError:
            return 0

    def validate_user_email(self, value):
        """Ensure email uniqueness"""
        if self.instance:
            if CustomUser.objects.filter(email=value).exclude(id=self.instance.user.id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        else:
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        user_email = validated_data.pop('user_email')
        password = validated_data.pop('password', 'defaultpassword123')  

        last_manager = Manager.objects.order_by('id').last()
        if last_manager and last_manager.employee_id:
            try:
                last_number = int(last_manager.employee_id.replace('MGR', ''))
                new_number = last_number + 1
            except (ValueError, TypeError):
                new_number = Manager.objects.count() + 1
        else:
            new_number = Manager.objects.count() + 1
        
        employee_id = f"MGR{new_number:03d}"

        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=user_email,
            username=user_email,
            role='manager'
        )
        user.set_password(password)
        user.save()

        return Manager.objects.create(user=user, employee_id=employee_id, **validated_data)

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        user_email = validated_data.pop('user_email', None)
        password = validated_data.pop('password', None)

        user = instance.user
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if user_email is not None and user_email != user.email:
            user.email = user_email
            user.username = user_email
        if password:
            user.set_password(password)
        user.save()

        return super().update(instance, validated_data)


from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class StaffSerializer(serializers.ModelSerializer):
    # Read-only convenience fields
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)

    # Write-only user fields (required for create)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    user_email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=False)  # Made optional

    class Meta:
        model = Staff
        fields = [
            'id', 'username', 'name', 'email',
            'manager', 'manager_name',
            'skill', 'employee_id', 'phone', 'status', 'joined_date',
            'created_at', 'updated_at',
            'first_name', 'last_name', 'user_email', 'password'
        ]
        read_only_fields = ['created_at', 'updated_at', 'manager_name', 'username', 'name', 'email', 'employee_id']

    def validate_user_email(self, value):
        """Ensure email uniqueness"""
        if self.instance:
            if CustomUser.objects.filter(email=value).exclude(id=self.instance.user.id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        else:
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        user_email = validated_data.pop('user_email')
        password = validated_data.pop('password', 'defaultpassword123')  # Default password

        
        last_staff = Staff.objects.order_by('id').last()
        if last_staff and last_staff.employee_id:
            try:
                last_number = int(last_staff.employee_id.replace('STF', ''))
                new_number = last_number + 1
            except (ValueError, TypeError):
                new_number = Staff.objects.count() + 1
        else:
            new_number = Staff.objects.count() + 1
        
        employee_id = f"STF{new_number:03d}"

        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=user_email,
            username=user_email,
            role='staff'
        )
        user.set_password(password)
        user.save()

        return Staff.objects.create(user=user, employee_id=employee_id, **validated_data)

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        user_email = validated_data.pop('user_email', None)
        password = validated_data.pop('password', None)

        user = instance.user
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if user_email is not None and user_email != user.email:
            user.email = user_email
            user.username = user_email
        if password:
            user.set_password(password)
        user.save()

        return super().update(instance, validated_data)



class CustomerSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'customer_id', 'name', 'email', 'phone', 'gender',
            'date_of_birth', 'profile_picture', 'profile_picture_url', 'status', 'added_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['customer_id', 'created_at', 'updated_at']

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def validate_email(self, value):
        instance = getattr(self, 'instance', None)
        if Customer.objects.filter(email=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        return value


class DashboardStatsSerializer(serializers.Serializer):
    total_managers = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    recent_customers = CustomerSerializer(many=True)
