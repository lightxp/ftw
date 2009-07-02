# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext
from ftw.context_processors import media_url

def index(request):
    
    return render_to_response('mapa/index/mapa.html', {
                                                 },
                            context_instance=RequestContext(request, processors=[media_url]))
