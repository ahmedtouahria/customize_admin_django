from __future__ import unicode_literals
import json
from django.contrib.auth import get_user_model
from django.contrib import admin
from .models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


        

class UserAdmin(BaseUserAdmin):
    def has_add_permission(self, request, obj=None):
        return request.user.is_admin
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin or (obj and obj.id == request.user.id)
    ##### function to display data in charts
    def changelist_view(self, request, extra_context=None):
        # Aggregate new user per day
        chart_data = (
            User.objects.annotate(date=TruncDay("created_at"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )
        partners_count = Profile.objects.filter(isPartner=True).count()
        count_users = User.objects.all().count() - partners_count
        user_qatar = User.objects.filter(country='QA').count()
        user_ksa = User.objects.filter(country='SA').count()
        user_kwait = User.objects.filter(country='KW').count()
        user_emarate = User.objects.filter(country='AE').count()
        user_others = count_users -(user_qatar+user_ksa+user_emarate+user_kwait)
        
        user = User.objects.get(name=request.user)
        print(user)
        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or  {
         "chart_data": as_json,
         "partners_count":partners_count,
         'count_users':count_users,
         'user_qatar':user_qatar,
         'user_ksa':user_ksa,
         'user_kwait':user_kwait,
         'user_emarate':user_emarate,
         'user_others':user_others,
         
         
         }
       

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)
    # The forms to add and change user instances
    model=User
    def has_add_permission(self, request, obj=None):
        return request.user.is_admin
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin or (obj and obj.id == request.user.id)

#####################################################################
    list_display = ('name', 'phone', 'admin','country')
    list_filter = ('staff','active' ,'admin', )
    fieldsets = (
    (None, {'fields': ('name','phone', 'password','country')}),
    ('Permissions', {'fields': ('admin', 'active', 'staff',)}), )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','country','phone', 'password1', 'password2')}
        ),
    )
    search_fields = ('phone','name')
    ordering = ('name',)
    filter_horizontal = ()

##############################################################################
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)
    
 ##############################################################################   
class ProfileAdmin(admin.ModelAdmin):
 list_display = ('user', 'city', 'isPartner')
 list_filter = ('city', 'isPartner')
 readonly_fields=('code',)

 
admin.site.register(User, UserAdmin)
admin.site.register(Profile,ProfileAdmin)

