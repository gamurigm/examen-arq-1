"""Descarga fotografias alternativas con atribucion; no modifica el catalogo SQL."""
import hashlib,html,json,pathlib,re,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/'assets/celulares/alternativas'
DEST.mkdir(parents=True,exist_ok=True)
HEAD={'User-Agent':'GR09Documentation/1.0 (educational documentation)'}
def read(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=40) as r:return r.read()
def clean(text):return html.unescape(re.sub('<[^>]+>','',text))
query=dict(action='query',format='json',generator='search',gsrsearch='smartphone filetype:bitmap',gsrnamespace=6,gsrlimit=50,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=900)
data=json.loads(read('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(query)))
manifest=[]
for page in data['query']['pages'].values():
 info=page['imageinfo'][0]; meta=info.get('extmetadata',{})
 license=meta.get('LicenseShortName',{}).get('value','')
 if not any(x in license for x in ['CC BY','CC0','Public domain']):continue
 url=info.get('thumburl',info['url'])
 if not re.search(r'\.(jpg|jpeg|png)(?:$|\?)',url,re.I):continue
 try:
  content=read(url)
  if not (content.startswith(b'\xff\xd8') or content.startswith(b'\x89PNG')):continue
  suffix='.jpg' if content.startswith(b'\xff\xd8') else '.png'
  name=f'foto-{len(manifest)+1:02d}'+suffix
  (DEST/name).write_bytes(content)
  manifest.append(dict(archivo=name,titulo=page['title'],autor=clean(meta.get('Artist',{}).get('value','')),fuente=info['descriptionurl'],descarga=url,licencia=license,licencia_url=meta.get('LicenseUrl',{}).get('value',''),sha256=hashlib.sha256(content).hexdigest(),cambios='Miniatura proporcionada por Wikimedia; sin edicion local'))
  (DEST/'fuentes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(name,flush=True)
  if len(manifest)==27:break
  time.sleep(.4)
 except Exception as e:print(type(e).__name__,flush=True)
if len(manifest)!=27:raise SystemExit('No se completaron las 27 fotografias adicionales')
