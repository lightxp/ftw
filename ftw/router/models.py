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
    przystanek_poczatkowy = models.ForeignKey('Przystanki', related_name="%(class)s_related")
    przystanek_koncowy = models.ForeignKey('Przystanki', related_name="%(class)ss_related")
    trasa = models.ForeignKey('Trasy', related_name="%(class)sr_related")
    
    class Meta:
        verbose_name_plural = "Linie"
    
    def __unicode__(self):
        return u'%s (%s)' % (self.nazwa_linii, self.kod)

class Przystanki(models.Model):     
    ulica = models.ForeignKey(Ulice)
    linia = models.ManyToManyField(Linie, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=8)
    lng = models.DecimalField(max_digits=10, decimal_places=8)
    nazwa_pomocnicza = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name_plural = "Przystanki"

    def __unicode__(self):
        return u'%s (%s)' % (self.ulica, self.nazwa_pomocnicza)

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
        return u"%d (%d min)" % (self.przystanki.count(),self.dlugosc_trasy)
    
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
    nocny = models.BooleanField()
    rozklad = models.ForeignKey(RozkladPrzystanek, related_name="%(class)s_related")
    
    def __unicode__(self):
        return "%s:%s" % (self.godzina, self.minuta)
    