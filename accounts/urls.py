from django.urls import path
from .views import index, user_login, user_signup, user_logout

urlpatterns = [
    path('', index, name='home'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
]