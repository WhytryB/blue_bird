from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings
from django.urls import reverse_lazy


from .forms import (
    SignInViaUsernameForm, ChangeProfileForm
)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class CountersView(LoginRequiredMixin, TemplateView):
    template_name = 'counters.html'


class CarsView(LoginRequiredMixin, TemplateView):
    template_name = 'cars.html'


class VoteView(LoginRequiredMixin, TemplateView):
    template_name = 'vote.html'


class ArchiveView(LoginRequiredMixin, TemplateView):
    template_name = 'archive.html'


class InfoView(LoginRequiredMixin, TemplateView):
    template_name = 'info.html'


class DocsView(LoginRequiredMixin, TemplateView):
    template_name = 'docs.html'


class SupportView(LoginRequiredMixin, TemplateView):
    template_name = 'support.html'


class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'profile.html'
    form_class = ChangeProfileForm

    def get_initial(self):
        user = self.request.user
        initial = super().get_initial()

        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        initial['middle_name'] = user.middle_name
        initial['mobile'] = user.mobile
        initial['email'] = user.email
        initial['address'] = user.address
        initial['profile_picture'] = user.profile_picture
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.middle_name = form.cleaned_data['middle_name']
        user.mobile = form.cleaned_data['mobile']
        user.email = form.cleaned_data['email']
        user.address = form.cleaned_data['address']
        user.profile_picture = form.cleaned_data['profile_picture']

        try:
            user.save()

            messages.success(self.request, _('Дані профілю успішно оновлено.'))
        except Exception as e:
            messages.error(self.request, str(e))  # Выводим сообщение об ошибке

        return redirect('profile')

    def form_invalid(self, form):
        # Добавляем ошибку в контекст, чтобы отобразить её в шаблоне
        for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(self.request, f'Помилка при оновленні профілю для поля {field}: {error}')

        return super().form_invalid(form)


class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LogInView(GuestOnlyView, FormView):
    template_name = 'login.html'

    @staticmethod
    def get_form_class(**kwargs):
        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request

        # If the test cookie worked, go ahead and delete it since its no longer needed
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()


        login(request, form.user_cache)

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())

        if url_is_safe:
            return redirect(redirect_to)

        return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form):
        # Добавляем ошибку в контекст, чтобы отобразить её в шаблоне
        return self.render_to_response(self.get_context_data(form=form, error='Неправильні облікові дані для входу'))


class CustomLogoutMixin:

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class LogOutView(CustomLogoutMixin, BaseLogoutView):
    next_page = reverse_lazy('login')

