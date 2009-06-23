from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice

def importuj(request):
    import csv
    listaUlic = csv.reader(open('s:/sources/phtdocs/ftw/poznan_ulice.csv'), quotechar='"')
    zlych = 0;

    for row in listaUlic:
      try:  
          u = Ulice(nazwa=row[0])
          u.save()
      except IndexError:
          zlych += 1    

    return render_to_response('admin/ulice/import.html', {
                                                'ile': listaUlic.line_num - zlych,
                                                 })
