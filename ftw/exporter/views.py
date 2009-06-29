# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import *
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