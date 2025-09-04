
from django.utils.dateparse import parse_date
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer, CustomUserSerializer, DepartmentSerializer,
    ManagerSerializer, StaffSerializer, CustomerSerializer, DashboardStatsSerializer
)
from .models import CustomUser, Department, Manager, Staff, Customer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



@api_view(['POST'])
@permission_classes([AllowAny])
def register_admin(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.role = 'admin'
        user.save()
        return Response({'message': 'Admin registered', 'user_id': user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    data = {
        'total_managers': Manager.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_departments': Department.objects.count(),
        'recent_customers': Customer.objects.order_by('-created_at')[:5],
    }
    serializer = DashboardStatsSerializer(data)  # pass as instance
    return Response(serializer.data, status=status.HTTP_200_OK)



def apply_date_range(queryset, field_name, request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    if from_date:
        d = parse_date(from_date)
        if d:
            queryset = queryset.filter(**{f'{field_name}__gte': d})
    if to_date:
        d = parse_date(to_date)
        if d:
            queryset = queryset.filter(**{f'{field_name}__lte': d})
    return queryset


def paginate(request, queryset, serializer_cls):
    paginator = PageNumberPagination()
    page_size = request.query_params.get('page_size')
    if page_size:
        try:
            paginator.page_size = int(page_size)
        except (ValueError, TypeError):
            pass

    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_cls(page, many=True)
    return paginator.get_paginated_response(serializer.data)

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def departments_list_create(request):
    if request.method == 'GET':
        qs = Department.objects.all()
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return paginate(request, qs, DepartmentSerializer)

    print("POST data received:", request.data)  # Debug line
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Serializer errors:", serializer.errors)  # Debug line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def department_detail(request, pk):
    try:
        obj = Department.objects.get(pk=pk)
    except Department.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(DepartmentSerializer(obj).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = DepartmentSerializer(obj, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def managers_list_create(request):
    if request.method == 'GET':
        qs = Manager.objects.select_related('user', 'department').all()
        search = request.query_params.get('search')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(team_name__icontains=search) |
                Q(department__name__icontains=search)
            )
            
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
            
        return paginate(request, qs, ManagerSerializer)

    print("POST data received:", request.data)  # Debug line
    serializer = ManagerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Serializer errors:", serializer.errors)  # Debug line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manager_detail(request, pk):
    try:
        obj = Manager.objects.select_related('user', 'department').get(pk=pk)
    except Manager.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ManagerSerializer(obj).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = ManagerSerializer(obj, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def staff_list_create(request):
    if request.method == 'GET':
        qs = Staff.objects.select_related('user', 'manager__user').all()
        search = request.query_params.get('search')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(skill__icontains=search) |
                Q(manager__user__first_name__icontains=search) |
                Q(manager__user__last_name__icontains=search)
            )
            
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
            
        return paginate(request, qs, StaffSerializer)

    print("POST data received:", request.data)  # Debug line
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Serializer errors:", serializer.errors)  # Debug line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def staff_detail(request, pk):
    try:
        obj = Staff.objects.select_related('user', 'manager__user').get(pk=pk)
    except Staff.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(StaffSerializer(obj).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = StaffSerializer(obj, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def customers_list_create(request):
    if request.method == 'GET':
        qs = Customer.objects.all()

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(customer_id__icontains=search)
            )

        status_param = request.query_params.get('status')
        if status_param:
            qs = qs.filter(status__iexact=status_param)

        gender = request.query_params.get('gender')
        if gender:
            qs = qs.filter(gender__iexact=gender)

        qs = apply_date_range(qs, 'added_date', request)
       
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CustomerSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = CustomerSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        instance = serializer.save()
        return Response(CustomerSerializer(instance, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def customer_detail(request, pk):
    try:
        obj = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({'detail': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CustomerSerializer(obj, context={'request': request}).data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = CustomerSerializer(obj, data=request.data, partial=(request.method == 'PATCH'), context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        obj.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def managers_dropdown(request):
    managers = Manager.objects.filter(status='active').select_related('user', 'department')
    data = [{'id': m.id, 'name': m.user.get_full_name(), 'department': m.department.name} for m in managers]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def departments_dropdown(request):
    depts = Department.objects.all().order_by('name')
    data = [{'id': d.id, 'name': d.name} for d in depts]
    return Response(data, status=status.HTTP_200_OK)
