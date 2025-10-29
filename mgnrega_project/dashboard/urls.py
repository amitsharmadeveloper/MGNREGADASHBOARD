from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('district/<str:state>/<str:district>/<str:year>/', views.district_dashboard, name='district_dashboard'),
    path('district/<str:state>/<str:district>/<str:year>/<str:month>/', views.district_dashboard, name='district_dashboard_month'),

]
