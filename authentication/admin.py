from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username', 
        'email',
    )
    list_display_links = ('id', 'username')
    list_per_page = 10
    
    search_fields = list_display
    

admin.site.register(User, UserAdmin)