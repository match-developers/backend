from django.urls import path

from .views import AllUsers, CreateAccount, CurrentUser

app_name = "users"

urlpatterns = [
    path("create/", CreateAccount.as_view(), name="create_user"),
    path("all/", AllUsers.as_view(), name="all"),
    path("current-user/", CurrentUser.as_view(), name="current"),
]
