from django.shortcuts import render_to_response, get_object_or_404
from ftw.router.models import Ulice
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required 

@staff_member_required
def importuj(request):
    import csv
    listaUlic = csv.reader(open(settings.IMPORT_DATA_ROOT + 'poznan_ulice.csv'), quotechar='"')
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
