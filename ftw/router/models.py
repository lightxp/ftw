# -*- coding: utf-8 -*- 
import sys

from django.db import models

# Create your models here.

class Ulice(models.Model):
  nazwa = models.CharField(max_length=250)

  class Meta:
        verbose_name_plural = "Ulice"
  
  def __unicode__(self):
    return self.nazwa

class Linie(models.Model):
    kod = models.CharField(max_length=20)
    nazwa_linii = models.CharField(max_length=200)
    trasa = models.ManyToManyField('Trasy')
    typ = models.ForeignKey('TypTrasy', related_name="typ_trasy") 
    
    class Meta:
        verbose_name_plural = "Linie"
    
    def __unicode__(self):
        return u'%s' % (self.kod)
    
    def getname(self):
        return u'%s' % (self.kod)
    
class Przystanki(models.Model):     
    kod = models.CharField(max_length=20)
    ulica = models.ForeignKey(Ulice, blank=True, null=True)
    linia = models.ManyToManyField(Linie, blank=True)
    lat = models.DecimalField(max_digits=14, decimal_places=12)
    lng = models.DecimalField(max_digits=14, decimal_places=12)
    nazwa_pomocnicza = models.CharField(max_length=100, blank=True)
    typ = models.ManyToManyField('TypTrasy') 
    
    class Meta:
        verbose_name_plural = "Przystanki"

    def __unicode__(self):
        return u'%s (%s)' % (self.nazwa_pomocnicza, self.kod)
    
    def getNearest(self, radius):
        #pobierz najblizsze, radius = km
        out = []
        if self.lat <= 0 or self.lng <=0:
            return out
         
        nearest = Przystanki.objects.extra(
                                   select={
                                           'distance': " 3959 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) " % (round(self.lat,5),round(self.lng,5),round(self.lat,5))}
                                   ).extra(
                                           order_by = ['distance']
                                           ).filter(lat__gt=0).filter(lng__gt=0).all()
        for item in nearest:
            if item.distance <= radius and item.distance > 0:
                temp = {
                            'kod'   :   item.kod,
                            'lat'   :   item.lat,
                            'lng'   :   item.lng,
                            'id'    :   item.id, 
                            'distance': item.distance, 
                        }
                out.append(temp)
        return out        

                    
class PrzystanekPozycja(models.Model):
    przystanek = models.ForeignKey(Przystanki, related_name="przystanek")
    pozycja = models.IntegerField()
    czas_dojazdu = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Przystanki/Pozycje"   
        
    def __unicode__(self):
        return u"%s. %s (%s min)" % (self.pozycja, self.przystanek, self.czas_dojazdu)     
    
class Trasy(models.Model):
    przystanki = models.ManyToManyField(PrzystanekPozycja)
    dlugosc_trasy = models.IntegerField()        

    class Meta:
        verbose_name_plural = "Trasy"

    def __unicode__(self):
        p = self.linie_set.all()[:1]
        for l in p:
            return u"%s %d/(%d min)" % (l.getname(), self.przystanki.count(), self.dlugosc_trasy)
        return u"Brak przypisania do linii; %d przystanki/(%d min)" % (self.przystanki.count(), self.dlugosc_trasy)

    def getFirst(self):
        return self.przystanki.order_by('pozycja')[:1].get().przystanek.nazwa_pomocnicza
    
    def getLast(self):
        return self.przystanki.order_by('-pozycja')[:1].get().przystanek.nazwa_pomocnicza
    
    def getLine(self):
        return self.linie_set.get().nazwa_linii
    
    def getType(self):
        return self.linie_set.get().typ.nazwa
    
    def getNextStopTime(self, przystanek, linia, h, m):
        p = self.przystanki.filter(pk=przystanek).get().przystanek
        rozkladp = RozkladPrzystanek.objects.filter(przystanek=p).filter(linia__kod=linia)
        rozklad = Rozklad.objects.filter(rozklad=rozkladp).filter(godzina__gte=h).filter(minuta__gt=m)
        from time import localtime, strftime
        day = localtime()[6]
        if day<5:
            rozklad = rozklad.filter(dzien_powszedni=True)
        if day==5:
            rozklad = rozklad.filter(sobota=True)
        if day==6:
            rozklad = rozklad.filter(niedziela=True)
        rozklad = rozklad.all()[:1]
        return rozklad
    
    def getBusList(self):
        return self.przystanki.all().order_by('pozycja')
    
class RozkladPrzystanek(models.Model):
    linia = models.ForeignKey(Linie)
    przystanek = models.ForeignKey(Przystanki)
    rozklad = models.ManyToManyField('Rozklad', blank=True)        

    class Meta:
        verbose_name_plural = "Rozklad->przystanek"

    def __unicode__(self):
        return u"%s: linia %s" % (self.przystanek, self.linia) 
    
class Rozklad(models.Model):
    godzina = models.IntegerField()
    minuta = models.IntegerField()
    dzien_powszedni = models.BooleanField()
    niedziela = models.BooleanField()
    sobota = models.BooleanField()
    rozklad = models.ForeignKey(RozkladPrzystanek, related_name="%(class)s_related")
    
    def __unicode__(self):
        return "%s:%s" % (self.godzina, self.minuta)
    
    class Meta:
        ordering = ["godzina","minuta"]
        
    def isNext(self):
        from time import localtime, strftime
        day = localtime()[6]
        h = strftime("%H", localtime())
        m = strftime("%M", localtime())
        
        if day<5 and not self.dzien_powszedni:
            return False
        if day==5 and not self.sobota:
            return False
        if day==6 and not self.niedziela:
            return False
        if self.godzina >= int(h)+1:
            return True
        if self.godzina >= int(h) and self.minuta > int(m):
            return True
        else:
            return False
    
class TypTrasy(models.Model):
    kod = models.CharField(max_length=2)
    nazwa = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.nazwa
    
    class Meta:
        verbose_name_plural = "Typy Tras"
                