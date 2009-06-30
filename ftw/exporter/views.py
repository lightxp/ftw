# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki
import xml.dom.minidom

def completeStreets(request, ulica_name):
    #zwraca liste ulic odpowiadajaca wywolaniu, nie mniej niz 3 znaki
    if len(ulica_name) < 3:
        return HttpResponse(status=404)
    
    doc = xml.dom.minidom.Document()
    ulice = Ulice.objects.all().filter(nazwa__icontains=ulica_name).order_by('nazwa')
    stor_ulice = doc.createElement('ulice')
    
    for ulica in ulice:
        stor_ulica = doc.createElement('ulica')
        stor_ulica.setAttribute('nazwa',ulica.nazwa)
        stor_ulice.appendChild(stor_ulica)
    
    doc.appendChild(stor_ulice)
    response = HttpResponse(mimetype='text/xml')
    response.write(doc.toxml())

    return response

def completeBusStops(request, przystanek_name):
    #zwraca liste dopasowanych przystankow
    if len(przystanek_name) < 3:
        return HttpResponse(status=404)
    
    doc = xml.dom.minidom.Document()
    przystanki = Przystanki.objects.filter(nazwa_pomocnicza__icontains=przystanek_name).order_by('nazwa_pomocnicza').distinct()
    stor_przystanki = doc.createElement('przystanki')
    
    for przystanek in przystanki:
        stor_przystanek = doc.createElement('przystanek')
        stor_przystanek.setAttribute('nazwa',przystanek.nazwa_pomocnicza)
        stor_przystanek.setAttribute('lat',str(przystanek.lat))
        stor_przystanek.setAttribute('lng',str(przystanek.lng))
        
        if przystanek.typ.count() > 0:
            stor_typy = doc.createElement('typy') 
            for typ in przystanek.typ.all():
               stor_typ = doc.createElement('typ') 
               stor_typ.setAttribute('nazwa',typ.nazwa)
               stor_typ.setAttribute('kod', typ.kod)
               stor_typy.appendChild(stor_typ)
            stor_przystanek.appendChild(stor_typy)

        if przystanek.linia.count() > 0:
            stor_linie = doc.createElement('linie') 
            for linia in przystanek.linia.all():
               stor_linia = doc.createElement('linia') 
               stor_linia.setAttribute('nazwa',linia.nazwa_linii)
               stor_linie.appendChild(stor_linia)
            stor_przystanek.appendChild(stor_linie)
                    
        stor_przystanki.appendChild(stor_przystanek)
    
    doc.appendChild(stor_przystanki)
    response = HttpResponse(mimetype='text/xml')
    response.write(doc.toxml())

    return response