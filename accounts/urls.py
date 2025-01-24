from django.urls import path
from . import views
app_name='accounts'

urlpatterns = [
    path('',views.register,name="accounts"),
    path('current_user/',views.current_user,name="current_user"),


]
