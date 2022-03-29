from django.contrib import admin
from .models import *


class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'title',
        'initial_price',
        'creation_time',
        'end_time',
        'ended_manually',
        'public',
    )
    list_display_links = ('id', 'title')
    list_per_page = 10
    
    search_fields = ('id', 'title', 'creation_time')
    
    
class BidAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'listing',
        'value',
        'creation_time',
    )
    list_display_links = ('id', 'value')
    list_per_page = 10

    search_fields = ('id', 'user', 'creation_time')
    
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'time',
        'body',
    )
    list_display_links = ('id',)
    list_per_page = 10
    
    search_fields = ('id', 'user')
    
    
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'time',
        'body',
    )
    list_display_links = ('id',)
    list_per_page = 10
    
    search_fields = ('id', 'author')


admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Category)