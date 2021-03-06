import locale
import os

from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.views.decorators.cache import cache_control

import settings
from althingi.models import *


def AccessDenied(Exception):
  pass


## Views ##

@cache_control(must_revalidate=False, max_age=900)
def index(request):
  t = loader.get_template('althingi/index.html')
  c = Context({
    'base': settings.TEMPLATE_BASE
  })
  return HttpResponse(t.render(c))

#@cache_control(must_revalidate=False, max_age=24*3600)
def thingmadur(request, althingi_id=None):
  try:
    thingmadur = Thingmadur.objects.filter(althingi_id=althingi_id)[0]
  except IndexError:
    thingmadur = None

  t = loader.get_template('althingi/thingmadur.html')
  return HttpResponse(t.render(Context({
    'base': settings.TEMPLATE_BASE,
    'thingmadur': thingmadur
  })))

#@cache_control(must_revalidate=False, max_age=24*3600)
def thingmenn(request):
  thingmenn = [{
    'thm': thm,
    'flokkur': thm.flokkur(),
    'flokksstafur': thm.flokkur().stafur,
    'skropari': False,
    'velmenni': False,
    'uppreisnarseggur': False
  } for thm in Thingmadur.objects.order_by('nafn')]

  thingmenn.sort(key=lambda t: float(t['thm'].maeting()))
  for ti in [t for t in thingmenn if not t['thm'].varamadur][:12]:
    ti['skropari'] = True

  thingmenn.sort(key=lambda t: float(t['thm'].hlydni()))
  for ti in [t for t in thingmenn if not t['thm'].varamadur][:12]:
    ti['uppreisnarseggur'] = True

  thingmenn.sort(key=lambda t: -(float(t['thm'].hlydni()) +
                                 float(t['thm'].maeting())))
  for ti in [t for t in thingmenn if not t['thm'].varamadur and
                                     not t['flokksstafur'] == '_'][:12]:
    ti['velmenni'] = True

  # Sort by name
  thingmenn.sort(key=lambda t: t['thm'].nafn, cmp=locale.strcoll)

  t = loader.get_template('althingi/thingmenn.html')
  return HttpResponse(t.render(Context({
    'base': settings.TEMPLATE_BASE,
    'flokkar': Flokkur.objects.order_by('nafn'),
    'thingmenn': thingmenn
  })))

#@cache_control(must_revalidate=False, max_age=3600)
def kosning(request, kosning_uid=None):
  try:
    kosning = Kosning.objects.filter(uid=kosning_uid)[0]
  except IndexError:
    kosning = None

  t = loader.get_template('althingi/kosning.html')
  return HttpResponse(t.render(Context({
    'base': settings.TEMPLATE_BASE,
    'kosning': kosning
  })))

#@cache_control(must_revalidate=False, max_age=3600)
def kosningar(request, year=None):
  kosningar = Kosning.objects.order_by('-umraeda__umfang')
  data = {
    'base': settings.TEMPLATE_BASE,
    'kosningar': kosningar
  }
  data['topp100'] = list(kosningar[:100])
  data['topp100'].sort(key=lambda k: k.timi)

  t = loader.get_template('althingi/kosningar.html')
  return HttpResponse(t.render(Context(data)))

@cache_control(must_revalidate=False, max_age=24*3600)
def static(request, filename):
  if '..' in filename:
    raise AccessDenied
  while filename.startswith('/'):
    filename = filename[1:]

  path = os.path.join(settings.RYNIR_DIR, 'althingi', 'static', filename)
  try:
    return HttpResponse(open(path, 'rb').read(),
                        mimetype=GuessMimeType(path))
  except:
    raise Http404()


## Helpers ##

def GuessMimeType(path):
  mimetype = 'application/octet-stream'
  if path.endswith('.png'):
    mimetype = 'image/png'
  elif path.endswith('.jpg'):
    mimetype = 'image/jpeg'
  elif path.endswith('.css'):
    mimetype = 'text/css'
  elif path.endswith('.js'):
    mimetype = 'text/javascript'
  return mimetype
