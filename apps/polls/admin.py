from django.contrib import admin

from models import Poll, PollItem


class PollItemInline(admin.TabularInline):
    model = PollItem
    extra = 0
    readonly_fields = ('vote_count',)
    
    
class PollAdmin(admin.ModelAdmin):
    inlines = [PollItemInline]
    

class PollItemAdmin(admin.ModelAdmin):
    readonly_fields = ('vote_count',)
    
    
admin.site.register(Poll, PollAdmin)
admin.site.register(PollItem, PollItemAdmin)