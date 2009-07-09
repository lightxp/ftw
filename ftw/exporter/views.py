# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki
import simplejson as json

def completeBusStopsXML(request, typIn):
    import xml.dom.minidom
    doc = xml.dom.minidom.Document()
    przystanki = Przystanki.objects.filter(typ__kod=typIn)
    stor_przystanki = doc.createElement('markers')
    
    for przystanek in przystanki:
        if(przystanek.lat > 0 and przystanek.lng > 0):
            stor_przystanek = doc.createElement('marker')
            stor_przystanek.setAttribute('name',przystanek.nazwa_pomocnicza)
            stor_przystanek.setAttribute('lat',str(przystanek.lat))
            stor_przystanek.setAttribute('lng',str(przystanek.lng))
            stor_przystanek.setAttribute('id',str(przystanek.id)) 
            stor_przystanek.setAttribute('linie',"|".join(przystanek.linia.values_list('nazwa_linii',flat=True)))                   
            stor_przystanki.appendChild(stor_przystanek)
    
    doc.appendChild(stor_przystanki)
    response = HttpResponse(mimetype='text/xml')
    response.write(doc.toxml())

    return response

def completeBusStops(request):
    #request.encoding = 'iso-8859-2'
    nazwa = request.GET.get('q')
    try:
    #zwraca liste dopasowanych przystankow
        if len(nazwa) < 3:
            return HttpResponse(status=200)
    except:
        return HttpResponse(status=404)
    out = []
    przystanki = Przystanki.objects.filter(nazwa_pomocnicza__icontains=nazwa).order_by('nazwa_pomocnicza').distinct()
    
    for przystanek in przystanki:
        przystanek_temp = {
                      'id':     przystanek.id,     
                      'name': przystanek.nazwa_pomocnicza,
                      'lat':    str(przystanek.lat),
                      'lng':    str(przystanek.lng),
                      'desc':   '',
                      }
        
        if przystanek.typ.count() > 0:
            przystanek_temp['desc'] += "%s" % (",".join(przystanek.typ.values_list('nazwa',flat=True)),)

        if przystanek.linia.count() > 0:
            przystanek_temp['desc'] += " Linie: %s" % (",".join(przystanek.linia.values_list('nazwa_linii',flat=True)),)

        out.append(przystanek_temp)

    ulice = Ulice.objects.all().filter(nazwa__icontains=nazwa).order_by('nazwa')
    
    for ulica in ulice:
        out.append({
                       'id':  ulica.id,
                      'name': ulica.nazwa,
                      'typ':  'UL',
                     })
    
    output = json.dumps(out)

    response = HttpResponse(mimetype='text/javascript')
    response.write(output)

    return response
    
def completeNearest(request, lat, lng, distance_max):
    import xml.dom.minidom
    doc = xml.dom.minidom.Document()
    stor_przystanki = doc.createElement('markers')

    przystanki = Przystanki.objects.extra(
                                   select={
                                           'distance': " 3959 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) " % (lat,lng,lat)}
                                   ).extra(
                                           order_by = ['distance']
                                           ).all()
   
    for przystanek in przystanki:
        if przystanek.distance <= distance_max and przystanek.distance > 0:
            if(przystanek.lat > 0 and przystanek.lng > 0):
                stor_przystanek = doc.createElement('marker')
                stor_przystanek.setAttribute('name',przystanek.nazwa_pomocnicza)
                stor_przystanek.setAttribute('lat',str(przystanek.lat))
                stor_przystanek.setAttribute('lng',str(przystanek.lng))
                stor_przystanek.setAttribute('id',str(przystanek.id)) 
                stor_przystanek.setAttribute('distance',str(przystanek.distance)) 
                stor_przystanek.setAttribute('linie',"|".join(przystanek.linia.values_list('nazwa_linii',flat=True)))                   
                stor_przystanki.appendChild(stor_przystanek)
    
    
    doc.appendChild(stor_przystanki)
    response = HttpResponse(mimetype='text/xml')
    response.write(doc.toxml())

    return response
       