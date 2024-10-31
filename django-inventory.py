# Django Inventory Management System Setup Instructions

## 1. Setup Virtual Environment and Django
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install django djangorestframework django-cors-headers

# Create Django project
django-admin startproject inventory_system
cd inventory_system

# Create Django app
python manage.py startapp inventory
```

## 2. Project Structure
inventory_system/
├── inventory_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
└── manage.py

## 3. Configure settings.py
```python
# inventory_system/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only
```

## 4. Create Models
```python
# inventory/models.py

from django.db import models

class InventoryItem(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"
```

## 5. Create Serializers
```python
# inventory/serializers.py

from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'sku', 'name', 'quantity', 'reorder_point', 'unit_price']
```

## 6. Create Views
```python
# inventory/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import InventoryItem
from .serializers import InventoryItemSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

    @action(detail=False, methods=['GET'])
    def low_stock(self, request):
        low_stock_items = InventoryItem.objects.filter(
            quantity__lte=F('reorder_point')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'])
    def quantity(self, request, pk=None):
        item = self.get_object()
        quantity_change = int(request.data.get('quantity_change', 0))
        item.quantity = F('quantity') + quantity_change
        item.save()
        item.refresh_from_db()
        serializer = self.get_serializer(item)
        return Response(serializer.data)
```

## 7. Configure URLs
```python
# inventory_system/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.urls')),
]

# inventory/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## 8. Register Admin
```python
# inventory/admin.py

from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'quantity', 'reorder_point', 'unit_price']
    search_fields = ['sku', 'name']
    list_filter = ['quantity', 'reorder_point']
```

## 9. Setup Database
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

## 10. Run Development Server
```bash
python manage.py runserver
```

API Endpoints:
- GET /api/inventory/ - List all items
- POST /api/inventory/ - Create new item
- GET /api/inventory/{id}/ - Get single item
- PUT /api/inventory/{id}/ - Update item
- DELETE /api/inventory/{id}/ - Delete item
- GET /api/inventory/low-stock/ - Get low stock items
- PUT /api/inventory/{id}/quantity/ - Update item quantity

Test the API using the Django admin interface at http://localhost:8000/admin/
