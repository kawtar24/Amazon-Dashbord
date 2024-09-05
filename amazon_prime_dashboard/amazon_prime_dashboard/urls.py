
from django.contrib import admin
from django.urls import path,include
import dashboard.urls


urlpatterns = [
    path ('', include(dashboard.urls)),
    path('admin/', admin.site.urls),
]
