from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.users.views import EmailTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.tests_app.urls')),
    path('api/', include('apps.careers.urls')),
    path('api/', include('apps.recommendations.urls')),
    path('api/', include('apps.reports.urls')),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
