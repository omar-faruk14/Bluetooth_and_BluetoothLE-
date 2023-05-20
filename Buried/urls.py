from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path, include #new


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home,name='home'),
    path("cal/", views.cal_bluetooth,name='bluetooth_finder'),
    path('ble-devices/', views.ble_devices, name='ble_devices'),
    path('bluetooth_scan/<str:device_address>/', views.bluetooth_scan, name='bluetooth_scan'),
    path('heatmap/', include('heatmap_ble.urls')),#new

]

