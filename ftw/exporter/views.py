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

def findWay(request,fromway,toway):
    #znajduje trase miedzy przystankami
    import pickle
    from ftw.exporter.dijkstar import find_path
    from time import localtime, strftime
    h = 8#strftime("%H", localtime())
    m = 20#strftime("%M", localtime())
            
    G = pickle.load(open(settings.IMPORT_DATA_ROOT + 'routes.poz', 'rb'))
    
    """for edge in G['edges']:
        e_przystanek = G['edges'][edge]['przystanek']
        e_trasa = G['edges'][edge]['trasa']
        e_linia = G['edges'][edge]['linia']
        item = PrzystanekPozycja.objects.filter(pk=e_przystanek).filter(trasy__pk=e_trasa).get()
        
        nastepny = item.trasy_set.get().getNextStopTime(przystanek=e_przystanek,linia=e_linia,type='P',h=h,m=m)
        if nastepny.count() > 0:
            ile_do_przesiadki = (nastepny.get().godzina * 60 + nastepny.get().minuta) - (int(h)*60 + int(m))
        else:
            ile_do_przesiadki = 0
            
        G['edges'][edge] = (item.czas_dojazdu+ile_do_przesiadki,)        
    """
    try:
        res = find_path(G,G, 'SOB-02', 'ZOO-22', calculateWeight)
        przystanki = res[0]
        edges = res[1]
        times = res[2]
        total_time = res[3]
        print total_time
    except NoPathError:
        res = []
            
    response = HttpResponse(mimetype='text/javascript')
    #response.write(json.dumps(out))

    return response    

def calculateWeight(v, e_attrs, prev_e_attrs):
    #dodatkowa funkcja
    #v - kod przystanku
    #e_attrs/prev_e_attrs atrybuty obecnego/poprzedniego wezla
    # czas_dojazdu, trasa.id, przystanek.id, linia.kod
    from time import localtime, strftime
    h = 8#strftime("%H", localtime())
    m = 20#strftime("%M", localtime())
    ile_do_przesiadki = 0
    
    """if e_attrs[3] != prev_e_attrs[3]:
        item = PrzystanekPozycja.objects.filter(pk=e_attrs[2]).filter(trasy__pk=e_attrs[1]).get()
        nastepny = item.trasy_set.get().getNextStopTime(przystanek=e_attrs[2],linia=e_attrs[3],type='P',h=h,m=m)
        
        if nastepny.count() > 0:
            ile_do_przesiadki = (nastepny.get().godzina * 60 + nastepny.get().minuta) - (int(h)*60 + int(m))
    """
    return e_attrs[0] + ile_do_przesiadki