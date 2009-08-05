# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki, Trasy, PrzystanekPozycja, TypTrasy
import simplejson as json
from django.conf import settings

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
       
       
def trasy(request):
    linia = request.GET.get('q')
    try:
        if len(linia) == 0:
            return HttpResponse(status=200)
    except:
        return HttpResponse(status=404)

    trasy = Trasy.objects.filter(linie__nazwa_linii__istartswith=linia)[:15]
    out = []
    
    for trasa in trasy:
       trasa_temp = {
                      'id'  :   trasa.id,     
                      'name':   trasa.getLine(),
                      'desc':   "%s z %s do %s" % (trasa.getType(),trasa.getFirst(),trasa.getLast()),
                      'przystanki'  :   '',
                    }

       if trasa.przystanki.count() > 0:
           przystanki = trasa.przystanki.all()
           przystanki_array = []
           for item in przystanki:
               przystanki_array.append({
                                       'id'    :   item.przystanek.id,
                                       'name'  :   item.przystanek.nazwa_pomocnicza,
                                       'lat'    :  str(item.przystanek.lat),
                                       'lng'    :  str(item.przystanek.lng),
                                       'linie'  :  "|".join(item.przystanek.linia.values_list('nazwa_linii',flat=True))
                                       })
           trasa_temp['przystanki'] = przystanki_array 
            
       out.append(trasa_temp)
        
    response = HttpResponse(mimetype='text/javascript')
    response.write(json.dumps(out))

    return response    

def findWay(request,fromway_lat,fromway_lng,toway_lat,toway_lng):
    #znajduje trase miedzy przystankami
    import pickle
    from ftw.exporter.dijkstar import find_path
    from time import localtime, strftime
    h = strftime("%H", localtime())
    m = strftime("%M", localtime())
    
    if int(h) > 22 or int(h) < 6:
        G = pickle.load(open(settings.IMPORT_DATA_ROOT + 'routes_night.poz', 'rb'))
    else:
        G = pickle.load(open(settings.IMPORT_DATA_ROOT + 'routes_day.poz', 'rb'))

    ile_tras = 3
    fromway = getNearestAdvenced(fromway_lat,fromway_lng,ile_tras)
    toway = getNearestAdvenced(toway_lat,toway_lng,ile_tras)

    routes = []
    for i in range(ile_tras):
        try:
            routes.append(find_path(G,G, fromway[i]['kod'], toway[i]['kod'], calculateWeight))
        except:
            pass
    
    #posortuj predkosci
    routes_speed = []
    for item in routes:
        routes_speed.append(item[3])        
    routes_speed.sort()    
    
    #przypisz najszybsza
    for item in routes:
        if item[3] == routes_speed[0]:
            res = item

    result = {}
    result['calkowity_czas'] = int(res[3]) * 60
    result['trasa'] = []

    for przystanek in res[0]:
        temp_przystanek = Przystanki.objects.filter(kod__iexact=przystanek).get()
        temp_dict = {
                     'id'       :   temp_przystanek.id,
                     'linie'    :   "|".join(temp_przystanek.linia.values_list('nazwa_linii',flat=True)),
                     'name'     :   temp_przystanek.nazwa_pomocnicza,
                     'lat'      :   str(temp_przystanek.lat),
                     'lng'      :   str(temp_przystanek.lng),
                     }
        result['trasa'].append(temp_dict)
        
    result['polaczenia'] = []    
    for polaczenie in res[1]:
        temp_polaczenie = G['edges'][polaczenie]
 
        temp_pol = {
                    'czas'  :   temp_polaczenie[0]
                    }
        if len(temp_polaczenie) > 1:
            temp_pol['linia'] = temp_polaczenie[3]
        else:
            temp_pol['linia'] = u'pieszo'
        result['polaczenia'].append(temp_pol)    

    response = HttpResponse(mimetype='text/javascript')
    response.write(json.dumps(result))
    return response    

def calculateWeight(v, e_attrs, prev_e_attrs):
    #dodatkowa funkcja
    #v - kod przystanku
    #e_attrs/prev_e_attrs atrybuty obecnego/poprzedniego wezla
    # czas_dojazdu, trasa.id, przystanek.id, linia.kod
    from time import localtime, strftime
    h = strftime("%H", localtime())
    m = strftime("%M", localtime())
    ile_do_przesiadki = 0
    
    if len(e_attrs)>1 and len(prev_e_attrs)>1 and e_attrs[3] != prev_e_attrs[3]:
        #przesiadka z jednego at na inny at
        item = PrzystanekPozycja.objects.filter(pk=e_attrs[2]).filter(trasy__pk=e_attrs[1]).get()
        nastepny = item.trasy_set.get().getNextStopTime(przystanek=e_attrs[2],linia=e_attrs[3],h=h,m=m)
        
        if nastepny.count() > 0:
            ile_do_przesiadki = (nastepny.get().godzina * 60 + nastepny.get().minuta) - (int(h)*60 + int(m))
    
    return e_attrs[0] + ile_do_przesiadki


def getNearestAdvenced(lat, lng, ile):
    #pobierz najblizsze przystanki
    out = []
    nearest = Przystanki.objects.extra(
                               select={
                                       'distance': " 3959 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) " % (round(float(lat),5),round(float(lng),5),round(float(lat),5))}
                               ).extra(
                                       order_by = ['distance']
                                       ).filter(lat__gt=0).filter(lng__gt=0).all()[:ile]
    for item in nearest:
        if item.distance > 0:
            temp = {
                        'kod'   :   item.kod,
                        'lat'   :   item.lat,
                        'lng'   :   item.lng,
                        'id'    :   item.id, 
                        'distance': item.distance, 
                    }
            out.append(temp)
    return out        