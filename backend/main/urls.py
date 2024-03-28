from django.urls import path
from . import views
from django.urls import re_path, include
from notifications import urls as notifications_urls

from .views import (
    LogInView, LogOutView, ChangeProfileView, HomeView, CountersView, PaymentView,
    CarsView, VoteView, ArchiveView, InfoView, DocsView, SupportView, execute_script, SetLichView, mark_notifications_as_read
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
    path('payment/', PaymentView.as_view(), name='payment'),
    path('login/', LogInView.as_view(), name='login'),
    path('set_lich/', SetLichView.as_view(), name='set_lich'),
    path('authorization_signature/', execute_script, name='execute_script'),
    path('logout/', LogOutView.as_view(), name='logout'),
    re_path(r'^inbox/notifications/', include(notifications_urls, namespace='notifications')),
    path('mark-as-read/', mark_notifications_as_read, name='mark_as_read'),
#     path('restore/password/', RestorePasswordView.as_view(), name='restore_password'),
#     path('restore/password/done/', RestorePasswordDoneView.as_view(), name='restore_password_done'),
#     path('change/password/', ChangePasswordView.as_view(), name='change_password'),
#     path('change/email/', ChangeEmailView.as_view(), name='change_email'),

]
