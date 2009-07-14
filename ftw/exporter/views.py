# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki, Trasy, PrzystanekPozycja
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

    trasy = Trasy.objects.filter(linie__nazwa_linii__icontains=linia)
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
    from dijkstar import find_path
    G = {
         'nodes'    :   {},
         'edges'    :   {},
         }
    
    trasy = Trasy.objects.all()
    
    for trasa in trasy:
        prev = ''
        for przystanek in trasa.przystanki.order_by('pozycja').all():
            if (prev):
                edge_name = 'l%st%s' % (trasa.getLine(),przystanek.czas_dojazdu)
                edge_name_curr = 'l%st%sc' % (trasa.getLine(),przystanek.czas_dojazdu)
                G['nodes'][str(przystanek.przystanek.kod)] = {}
                
                G['nodes'][str(prev.przystanek.kod)][str(przystanek.przystanek.kod)] =  edge_name
                G['edges'][edge_name] = (przystanek.czas_dojazdu,)

                G['nodes'][str(przystanek.przystanek.kod)][str(prev.przystanek.kod)] =  edge_name_curr
                G['edges'][edge_name_curr] = (przystanek.czas_dojazdu,)
            else:
                G['nodes'][str(przystanek.przystanek.kod)] = {}    
            prev = przystanek        
            
            
    #print G
    """G = {
            'nodes': {  # Adjacency matrix
                1: {2: 'e1'},  # Vertex v goes to vertex u via edge e
                2: {1: 'e1', 3:'e2', 4:'e3'},
                3: {2: 'e2',4: 'e3' },
                4: {2:  'e3'},
             },

             'edges': {  # Edge attributes
                 'e1': (1,),  # Edge e's attributes
                 'e2': (10,),  # Edge e's attributes
                 'e3':  (2,),
             }
         }
    """
    res = find_path(G,G, 'SZYM-01', 'GORC-02')
    print res
    response = HttpResponse(mimetype='text/javascript')
    #response.write(json.dumps(out))

    return response    
    