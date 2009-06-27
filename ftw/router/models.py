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
        return u'%s (%s)' % (self.nazwa_linii, self.kod)
    
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
    
class RozkladPrzystanek(models.Model):
    linia = models.ForeignKey(Linie)
    przystanek = models.ForeignKey(Przystanki)
    rozklad = models.ManyToManyField('Rozklad', blank=True)        

    class Meta:
        verbose_name_plural = "Rozklad->przystanek"

    def __unicode__(self):
        return u"%s :linia %s)" % (self.przystanek, self.linia) 
    
class Rozklad(models.Model):
    godzina = models.CharField(max_length=2)
    minuta = models.CharField(max_length=2)
    dzien_powszedni = models.BooleanField()
    niedziela = models.BooleanField()
    sobota = models.BooleanField()
    rozklad = models.ForeignKey(RozkladPrzystanek, related_name="%(class)s_related")
    
    def __unicode__(self):
        return "%s:%s" % (self.godzina, self.minuta)
    
class TypTrasy(models.Model):
    kod = models.CharField(max_length=2)
    nazwa = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.nazwa
    
    class Meta:
        verbose_name_plural = "Typy Tras"
                