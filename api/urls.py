from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path("databases/", views.databases, name="databases"),
    path("databases/<str:name>", views.database_names, name="databases_name"),

    path('blueprints/', views.table_blue_prints),
    path('blueprints/<str:name>/', views.table_blue_print),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register, name='register_user'),
    path('usernames/<str:username>', views.usernames, name='usernames'),
    
    path('<str:database_name>/<str:blueprint_name>/', views.table_instances),
    path('<str:database_name>/<str:blueprint_name>/<str:filters>', views.table_instance),
]