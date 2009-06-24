from ftw.router.models import *
from django.contrib import admin

class UliceAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ['nazwa']
    ordering = ['nazwa']

class PrzystankiAdmin(admin.ModelAdmin):
    list_display = ('nazwa_pomocnicza','kod')
    search_fields = ['nazwa_pomocnicza', 'kod']
    ordering = ['nazwa_pomocnicza']

class RozkladInlines(admin.TabularInline):
    model = Rozklad
    extra = 30

class RozkladPrzystankiAdmin(admin.ModelAdmin):
    inlines = [RozkladInlines]
    fieldsets = [
        (None,               {'fields': ['linia','przystanek']})
    ,]

    
admin.site.register(Ulice,UliceAdmin)
admin.site.register(Linie)
admin.site.register(Przystanki,PrzystankiAdmin)
admin.site.register(RozkladPrzystanek, RozkladPrzystankiAdmin)
admin.site.register(Trasy)
admin.site.register(PrzystanekPozycja)
admin.site.register(TypTrasy)