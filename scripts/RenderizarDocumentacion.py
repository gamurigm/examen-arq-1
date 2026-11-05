"""Renderiza borradores a PDF y PNG sin modificar entregables finales."""
import argparse, hashlib, json, pathlib, subprocess
import fitz
from PIL import Image, ImageDraw
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--renderer',choices=['com','soffice'],default='soffice');parser.add_argument('--soffice',default='soffice.com');parser.add_argument('--skip-conversion',action='store_true');args=parser.parse_args()
profile=json.loads((root/'documentation-profile.json').read_text(encoding='utf-8'))
drafts=pathlib.Path(profile['documentation']['draft_directory']);dest=pathlib.Path(profile['documentation']['render_directory']);dest.mkdir(parents=True,exist_ok=True)
manifest_path=drafts/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
files=[pathlib.Path(a['draft']) for a in manifest['artifacts']]
if not args.skip_conversion:
    if args.renderer=='com':
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'scripts/RenderizarOffice.ps1'),'-DraftDirectory',str(drafts),'-RenderDirectory',str(dest),'-FilesJson',json.dumps([f.name for f in files])],check=True)
    else:
        word_files=[f for f in files if f.suffix.casefold()=='.docx']
        if word_files:
            subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'scripts/RenderizarOffice.ps1'),'-DraftDirectory',str(drafts),'-RenderDirectory',str(dest),'-FilesJson',json.dumps([f.name for f in word_files]),'-UpdateFieldsOnly'],check=True)
        office_profile=dest/'libreoffice-profile';office_profile.mkdir(parents=True,exist_ok=True)
        subprocess.run([args.soffice,'-env:UserInstallation='+office_profile.resolve().as_uri(),'--headless','--convert-to','pdf','--outdir',str(dest),*[str(f) for f in files]],check=True)
records=[]
for file in files:
    pdf=dest/(file.stem+'.pdf')
    if not pdf.is_file() or pdf.stat().st_mtime<file.stat().st_mtime:raise RuntimeError('PDF ausente o desactualizado: '+str(pdf))
    doc=fitz.open(pdf);thumbs=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1,1));pix.save(str(dest/(file.stem+f'_p{i+1:02}.png')))
        img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);img.thumbnail((400,550))
        tile=Image.new('RGB',(420,585),'#ddd');tile.paste(img,(10,25));ImageDraw.Draw(tile).text((10,5),f'Página {i+1}',fill='black');thumbs.append(tile)
    contact_sheets=[]
    for start in range(0,len(thumbs),12):
        chunk=thumbs[start:start+12]
        sheet=Image.new('RGB',(1260,585*((len(chunk)+2)//3)),'white')
        for i,img in enumerate(chunk):sheet.paste(img,((i%3)*420,(i//3)*585))
        output=dest/(file.stem+f'_contacto_{start//12+1:02}.png');sheet.save(output);contact_sheets.append(str(output))
    records.append({'archivo':str(pdf),'paginas':len(doc),'contact_sheets':contact_sheets})
(dest/'render-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for artifact in manifest['artifacts']:
    draft=pathlib.Path(artifact['draft'])
    artifact['draftSha256']=hashlib.sha256(draft.read_bytes()).hexdigest()
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
