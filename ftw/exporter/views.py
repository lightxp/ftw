# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki
import simplejson as json

from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote


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
