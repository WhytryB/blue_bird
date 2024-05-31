from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Poll, Choice, Vote, PhotoModel, SupportTicket, BackgroundModel, DIA, EnvFile
from django.http import HttpResponseRedirect
from django.urls import path
import subprocess


class EnvFileAdmin(admin.ModelAdmin):
    change_list_template = "admin/envfile_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('save_env/', self.admin_site.admin_view(self.save_env), name='save_env')
        ]
        return custom_urls + urls

    def save_env(self, request):
        if request.method == 'POST':
            content = request.POST['content']
            with open('.env', 'w') as f:
                f.write(content)
            self.restart_server()
            self.message_user(request, "Environment file updated and server restarted.")
            return HttpResponseRedirect("../")

    def restart_server(self):
        import os
        subprocess.Popen(["sudo", "systemctl", "restart", "gunicorn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True

    def changelist_view(self, request, extra_context=None):
        # Ensure we load the content of the .env file when we load the change list page
        extra_context = extra_context or {}
        with open('.env', 'r') as f:
            extra_context['content'] = f.read()
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(EnvFile, EnvFileAdmin)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_picture')

admin.site.register(CustomUser, CustomUserAdmin)


class ChoiceInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Choice
    extra = 1


class PhotoModelInline(admin.TabularInline):
    model = PhotoModel
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ["text",  "pub_date", "active", "created_at"]
    search_fields = ["text"]
    list_filter = ["active", 'created_at', 'pub_date']
    date_hierarchy = "pub_date"
    inlines = [ChoiceInline, PhotoModelInline]


@admin.register(PhotoModel)
class PhotoModelAdmin(admin.ModelAdmin):
    list_display = ["title", "photo"]
    search_fields = ["title"]
    autocomplete_fields = ["poll"]


@admin.register(BackgroundModel)
class BackgroundModelAdmin(admin.ModelAdmin):
    list_display = ["title", "photo", "photo_type"]
    search_fields = ["title"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["choice_text", "poll", 'created_at', 'updated_at']
    search_fields = ["choice_text", "poll__text"]
    autocomplete_fields = ["poll"]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["choice", "poll", "user", 'created_at']
    search_fields = ["choice__choice_text", "poll__text", "user__username"]
    autocomplete_fields = ["choice", "poll", "user"]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ["category", "description", 'created_at']
    search_fields = ["category", "description"]


@admin.register(DIA)
class DIAAdmin(admin.ModelAdmin):
    search_fields = ["request_id"]