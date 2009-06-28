# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import *
from ftw.importer.models import Events
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required 

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

@staff_member_required
def importuj_ulice(request):
    import csv
    listaUlic = csv.reader(open(settings.IMPORT_DATA_ROOT + 'poznan_ulice.csv'), quotechar='"')
    Ulice.objects.all().delete()
    zlych = 0;

    for row in listaUlic:
      try:  
          u = Ulice(nazwa=row[0])
          u.save()
      except IndexError:
          zlych += 1    

    return render_to_response('admin/import/status.html', {
                                                'ile': listaUlic.line_num - zlych,
                                                'czego': 'ulic',
                                                 })

@staff_member_required
def importuj_przystanek(request):
    import csv
    listaPrzystankow = csv.reader(open(settings.IMPORT_DATA_ROOT + 'przystanki.csv'), quotechar='"')
    zlych = 0;
    Przystanki.objects.all().delete()
    
    for row in listaPrzystankow:
      try:  
          p = Przystanki(nazwa_pomocnicza=row[1], kod=row[0], lat=row[3], lng=row[4])
          p.save()
          typy = row[2].split('|')
          for typ_item in typy:
              tempTyp = TypTrasy.objects.get(kod__exact=typ_item)
              p.typ.add(tempTyp)
          p.save()    
      except IndexError:
          zlych += 1    

    return render_to_response('admin/import/status.html', {
                                                'ile': listaPrzystankow.line_num - zlych,
                                                'czego': 'przystankow',
                                                 })

@staff_member_required
def importuj_trasy(request):
    #import trasy z pliku XML wygenerowanego wg standardu MPK Poznan
    rozklad_file_name = settings.IMPORT_DATA_ROOT + 'Rozklady.xml'
    # usuniecie wszystkich danych o trasach oraz rozkladach i liniach
    try: 
        Linie.objects.all().delete()  
        PrzystanekPozycja.objects.all().delete()
        Trasy.objects.all().delete()
        Rozklad.objects.all().delete()
        RozkladPrzystanek.objects.all().delete()
          
        parser = make_parser()
        parser.setContentHandler(trasaHandler())
        parser.parse(rozklad_file_name);
        status = True
    except:    
        status = False

    event = Events(file_name=rozklad_file_name, state=status)
    event.save()
    
    return render_to_response('admin/import/status.html', {
                                                'czego': 'tras',
                                                 })

class trasaHandler(ContentHandler):
    inLines = False
    inLine = False
    inDirection = False
    inStop = False
    inLegend = False
    inHour = False
    
    lineNumber = 0
    stopKod = ''
    stopName = ''
    stopId = 0
    stopPosition = 1
    stopRozklad = ''
    
    trasa = ''
    linia = ''
    pp = ''
    
    current_hour = 0
    current_hour_key = ''
    current_minute = 0
    inDP = False
    #obliczanie czasu dojazdu
    calkowita_trasa = 0
    valid = {}
    lastStamp = 0
    
    def startElement(self, name, attributes):
        if name == 'lines':
            #Linie
            self.inLines = True
        
        if name == 'line':
            #Linia
            self.inLine = True
            self.lineNumber = attributes.getValue('name')
            
            #tylko dla poznania
            try:
                if int(self.lineNumber) > 26:
                    tempTyp = 'A'
                else:
                    tempTyp = 'T'
            except:
                tempTyp = 'A'        
                    
            self.linia = Linie(kod = self.lineNumber, nazwa_linii = self.lineNumber, typ = TypTrasy.objects.get(kod__exact=tempTyp))
            self.linia.save()

        if name == 'direction':
            #kierunek - pojedyncza linia
            self.inDirection = True
            self.trasa = Trasy(dlugosc_trasy = 0)
            self.trasa.save()  

        if name == 'stop':
            #przystanek do konkretnej direction/linii
            self.inStop = True
            self.stopKod = attributes.getValue('id') 
            self.stopName = attributes.getValue('name') 
            
            #update nazwy przystanku wg kodu
            try:
                p = Przystanki.objects.get(kod=self.stopKod)
                p.nazwa_pomocnicza = self.stopName
                p.save()
                self.stopId = p.id
            except:      
                #brak przystanku na liscie, dodaj nowy
                p = Przystanki(kod = self.stopKod, nazwa_pomocnicza = self.stopName, lat = 0, lng = 0)
                tempTyp = TypTrasy.objects.get(kod__exact='?')
                p.save()
                p.typ.add(tempTyp)
                p.save()
                self.stopId = p.id

            #dodaj przystanek do trasy
            self.pp = PrzystanekPozycja(przystanek = p, pozycja = self.stopPosition, czas_dojazdu = 0)
            self.pp.save()
            self.trasa.przystanki.add(self.pp)
            self.stopPosition += 1
            
            #dodaj rozklad do przytanku
            self.stopRozklad = RozkladPrzystanek(linia = self.linia, przystanek = p)
            self.stopRozklad.save()
            
        if name == 'hour':
            #godzina
            self.inHour = True
            self.current_hour = attributes.getValue('value')
            self.current_hour_key = self.current_hour
            if int(self.current_hour) < 10:
                self.current_hour_key = "0%s" % (self.current_hour)
            self.valid[self.current_hour_key] = []    
                
        if name == 'minute':
            #minuty do godziny
            type = attributes.getValue('type')
            minuta_xml = attributes.getValue('value')
            
            dp = False
            nd = False
            s = False
            
            if(type == u'Dni powszednie'):
                dp = True
                self.valid[self.current_hour_key].append(minuta_xml)
                self.inDP = True
                
            if(type == u'Soboty'):
                s = True
                self.inDP = False
                
            if(type == u'Niedziele i święta'):
                nd = True
                self.inDP = False
            
            r = Rozklad(godzina=self.current_hour, minuta = minuta_xml, dzien_powszedni = dp, niedziela = nd, sobota = s, rozklad = self.stopRozklad)
            r.save()
            self.stopRozklad.rozklad.add(r);
        if name == 'legend' and self.inDP:
            self.valid[self.current_hour_key].pop()
                        
    def endElement(self, name):
        if name == 'lines':
            self.inLines = False

        if name == 'line':
            #zapisujemy gotowa linie wraz z trasami
            self.linia.save() 
            self.inLine = False

        if name == 'direction':
            self.inDirection = False
            #ustaw 1 na pozycji  
            self.stopPosition = 1
            #zapisujemy trase i dodajemy ja do linii
            self.trasa.dlugosc_trasy = self.calkowita_trasa  
            self.trasa.save()
            self.linia.trasa.add(self.trasa)
            
        if name == 'stop':
            #przystanek do konkretnej direction/linii
            self.inStop = False
            tempStamp = self.lastStamp
            godziny = self.valid.keys()
            godziny.sort()
            godziny.reverse()
            
            if len(self.valid[godziny[0]]) == 0:
                temp = self.valid[godziny[1]]
                hour = godziny[1]
            else:
                temp = self.valid[godziny[0]]   
                hour = godziny[0] 

            temp.reverse()
            self.lastStamp = int(hour) *60 + int(temp[0])  
            if tempStamp == 0:
                tempStamp = self.lastStamp
                
            czas_dojazdu = self.lastStamp - tempStamp
            print "%s min; linia:%s przystanek: %s" % (czas_dojazdu,self.lineNumber, self.stopKod)
            if czas_dojazdu < 0:
                czas_dojazdu = 0
            self.valid = {}
            self.calkowita_trasa += czas_dojazdu
            self.pp.czas_dojazdu = czas_dojazdu
            self.pp.save()
            #zapisz rozklady do przystanku
            self.stopRozklad.save()

        if name == 'hour':
            #przystanek do konkretnej direction/linii
            self.inHour = False

            self.current_hour = 0     
            self.stopRozklad.save()
        
    def characters(self, content):
        if self.inLegend == True:
            #print "Content:" + content
           pass         
