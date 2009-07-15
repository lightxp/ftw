# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext
from ftw.context_processors import media_url
from ftw.router.models import *

def index(request):
    
    return render_to_response('mapa/index/mapa.html', {
                                                 },
                            context_instance=RequestContext(request, processors=[media_url]))

def rozkladGenerate(request, przystanek, linia):
    rozklad_obj = RozkladPrzystanek.objects.filter(linia__nazwa_linii=linia).filter(przystanek__id=przystanek).get()
    #for rozklad in rozklad_obj:
    dp = {}
    for item in rozklad_obj.rozklad.filter(dzien_powszedni=True).order_by('minuta').order_by('godzina'):
        if not dp.has_key(item.godzina):
            dp[item.godzina] = ''
        dp[item.godzina] += str(item.minuta) + ', '
    
    sb = {}
    for item in rozklad_obj.rozklad.filter(sobota=True).order_by('minuta').order_by('godzina'):
        if not sb.has_key(item.godzina):
            sb[item.godzina] = ''
        sb[item.godzina] += str(item.minuta) + ', '

    nd = {}
    for item in rozklad_obj.rozklad.filter(niedziela=True).order_by('minuta').order_by('godzina'):
        if not nd.has_key(item.godzina):
            nd[item.godzina] = ''
        nd[item.godzina] += str(item.minuta) + ', '

    tr = Trasy.objects.filter(przystanki__przystanek=przystanek).filter(linie__nazwa_linii=linia).get()
    
    return render_to_response('mapa/index/rozklad.html', {
                                                          'nazwa':       rozklad_obj,
                                                          'pierwszy':    tr.getFirst(),
                                                          'ostatni':     tr.getLast(),
                                                          'rozklad_pp': dp,
                                                          'rozklad_sb': sb,
                                                          'rozklad_nd': nd,
                                                 },
                            context_instance=RequestContext(request, processors=[media_url]))