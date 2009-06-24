from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice, Przystanki,TypTrasy
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required 

@staff_member_required
def importuj(request):
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
