# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import *
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

    # usuniecie wszystkich danych o trasach oraz rozkladach i liniach
    Linie.objects.all().delete()  
    PrzystanekPozycja.objects.all().delete()
    Trasy.objects.all().delete()
    Rozklad.objects.all().delete()
    RozkladPrzystanek.objects.all().delete()
      
    parser = make_parser()
    parser.setContentHandler(trasaHandler())
    parser.parse(settings.IMPORT_DATA_ROOT + 'Rozklady.xml');
    
    return render_to_response('admin/import/status.html', {
                                                #'ile': listaPrzystankow.line_num - zlych,
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
    
    current_hour = 0
    
    def startElement(self, name, attributes):
        if name == 'lines':
            #Linie
            self.inLines = True
        
        if self.inLines == True and name == 'line':
            #Linia
            self.inLine = True
            self.lineNumber = attributes.getValue('name')
            self.linia = Linie(kod = self.lineNumber, nazwa_linii = self.lineNumber, typ = TypTrasy.objects.get(kod__exact='?'))
            self.linia.save() 
        
        if self.inLines == True and self.inLine == True and name == 'direction':
            #kierunek - pojedyncza linia
            self.inDirection = True
            self.trasa = Trasy(dlugosc_trasy = 0)
            self.trasa.save()  

        if self.inLines == True and self.inLine == True and self.inDirection == True and name == 'stop':
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
            #TODO: obliczyc czas dojazdu
            pp = PrzystanekPozycja(przystanek = p, pozycja = self.stopPosition, czas_dojazdu = 0)
            pp.save()
            self.trasa.przystanki.add(pp)
            self.stopPosition += 1
            
            #dodaj rozklad do przytanku
            self.stopRozklad = RozkladPrzystanek(linia = self.linia, przystanek = p)
            self.stopRozklad.save()
            
        if self.inLines == True and self.inLine == True and self.inDirection == True and self.inStop == True and name == 'hour':
            #przystanek do konkretnej direction/linii
            self.inHour = True
            self.current_hour = attributes.getValue('value')      

        if self.inLines == True and self.inLine == True and self.inDirection == True and self.inStop == True and self.inHour == True and name == 'minute':
            #przystanek do konkretnej direction/linii
            type = attributes.getValue('type')
            minuta_xml = attributes.getValue('value')
            
            dp = False
            nd = False
            s = False
            
            if(type == u'Dni powszednie'):
                dp = True
                
            if(type == u'Soboty'):
                s = True
                
            if(type == u'Niedziele i święta'):
                nd = True
            
            r = Rozklad(godzina=self.current_hour, minuta = minuta_xml, dzien_powszedni = dp, niedziela = nd, sobota = s, rozklad = self.stopRozklad)
            r.save()
            self.stopRozklad.rozklad.add(r);      
            
    def endElement(self, name):
        if name == 'lines':
            self.inLines = False

        if self.inLines == True and name == 'line':
            #zapisujemy gotowa linie wraz z trasami
            self.linia.save() 
            self.inLine = False

        if self.inLines == True and self.inLine == True and name == 'direction':
            self.inDirection = False
            #ustaw 1 na pozycji  
            self.stopPosition = 1
            #zapisujemy trase i dodajemy ja do linii
            self.trasa.save()
            self.linia.trasa.add(self.trasa)
            
        if self.inLines == True and self.inLine == True and self.inDirection == True and name == 'stop':
            #przystanek do konkretnej direction/linii
            self.inStop = False
            
            #zapisz rozklady do przystanku
            self.stopRozklad.save()

        if self.inLines == True and self.inLine == True and self.inDirection == True and self.inStop == True and name == 'hour':
            #przystanek do konkretnej direction/linii
            self.inHour = False
            self.current_hour = 0     
            self.stopRozklad.save()
        
    def characters(self, content):
        if self.inLegend == True:
            #print "Content:" + content
           pass         
