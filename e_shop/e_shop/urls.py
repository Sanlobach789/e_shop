"""e_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, re_path, include

from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from authapp.views_api import ActivateUserViewSet
from mainapp.views_api import CategoryModelViewSet, ItemModelViewSet
from basketapp.views_api import BasketModelViewSet
from ordersapp.views_api import OrderModelViewSet
from e_shop.settings import MEDIA_URL, MEDIA_ROOT


router = DefaultRouter()
router.register('api/categories', CategoryModelViewSet)
router.register('api/categories/(?P<category_id>[0-9]+)/items', ItemModelViewSet)
router.register('api/basket', BasketModelViewSet, basename='basket')
router.register('api/order', OrderModelViewSet, basename='order')

schema_view = get_schema_view(
    openapi.Info(
        title='e_shop',
        default_version='0.1',
        description='Documentation to out project',
    ),
    public=True,
    permission_classes=[AllowAny]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
    path('auth/users/activation/<uid>/<token>/',
         ActivateUserViewSet.as_view({'get': 'activation'})),
    path('', include(router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
