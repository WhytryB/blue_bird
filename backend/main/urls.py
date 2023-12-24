from django.urls import path
from . import views
from .views import (
    LogInView, LogOutView, ChangeProfileView, HomeView, CountersView,
    CarsView, VoteView, ArchiveView, InfoView, DocsView, SupportView,
#     ChangeEmailView, ChangeProfileView, ChangePasswordView,
#     RestorePasswordView, RestorePasswordDoneView,
)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('counters/', CountersView.as_view(), name='counters'),
    path('cars/', CarsView.as_view(), name='cars'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('archive/', ArchiveView.as_view(), name='archive'),
    path('info/', InfoView.as_view(), name='info'),
    path('docs/', DocsView.as_view(), name='docs'),
    path('support/', SupportView.as_view(), name='support'),
    path('profile/', ChangeProfileView.as_view(), name='profile'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
#     path('restore/password/', RestorePasswordView.as_view(), name='restore_password'),
#     path('restore/password/done/', RestorePasswordDoneView.as_view(), name='restore_password_done'),
#     path('change/password/', ChangePasswordView.as_view(), name='change_password'),
#     path('change/email/', ChangeEmailView.as_view(), name='change_email'),

]
