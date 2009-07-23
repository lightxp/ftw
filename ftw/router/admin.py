from ftw.router.models import *
from django.contrib import admin

class UliceAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ['nazwa']
    ordering = ['nazwa']

class LinieAdmin(admin.ModelAdmin):
    list_display = ('kod','typ',)
    search_fields = ['kod','typ']
    ordering = ['kod']
    actions= ['make_as_night']
    def make_as_night(modeladmin, request, queryset):
        queryset.update(typ=TypTrasy.objects.filter(kod__exact='N').get())
    make_as_night.short_description = "Oznacz jako Nocny"


class PrzystankiAdmin(admin.ModelAdmin):
    list_display = ('nazwa_pomocnicza','kod','lat','lng')
    search_fields = ['nazwa_pomocnicza', 'kod']
    ordering = ['nazwa_pomocnicza']

class RozkladInlines(admin.TabularInline):
    model = Rozklad
    extra = 3

class RozkladPrzystankiAdmin(admin.ModelAdmin):
    inlines = [RozkladInlines]
    search_fields = ['linia', 'przystanek']
    list_display = ('linia','przystanek')
    fieldsets = [
        (None,               {'fields': ['linia','przystanek']})
    ,]

    
admin.site.register(Ulice,UliceAdmin)
admin.site.register(Linie, LinieAdmin)
admin.site.register(Przystanki,PrzystankiAdmin)
admin.site.register(RozkladPrzystanek, RozkladPrzystankiAdmin)
admin.site.register(Trasy)
admin.site.register(PrzystanekPozycja)
admin.site.register(TypTrasy)