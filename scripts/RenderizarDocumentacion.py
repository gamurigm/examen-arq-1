"""Renderiza borradores a PDF y PNG sin modificar entregables finales."""
import argparse, json, pathlib, subprocess
import fitz
from PIL import Image, ImageDraw
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--soffice',default='D:/tools/LibreOffice/program/soffice.exe');args=parser.parse_args()
profile=json.loads((root/'documentation-profile.json').read_text(encoding='utf-8'))
drafts=pathlib.Path(profile['documentation']['draft_directory']);dest=pathlib.Path(profile['documentation']['render_directory']);dest.mkdir(parents=True,exist_ok=True)
files=[pathlib.Path(a['draft']) for a in json.loads((drafts/'manifest.json').read_text(encoding='utf-8'))['artifacts']]
subprocess.run([args.soffice,'-env:UserInstallation=file:///D:/tools/LibreOfficeProfile-CelularGR09-QA','--headless','--convert-to','pdf','--outdir',str(dest),*[str(f) for f in files]],check=True)
records=[]
for file in files:
    pdf=dest/(file.stem+'.pdf')
    if not pdf.is_file() or pdf.stat().st_mtime<file.stat().st_mtime:raise RuntimeError('PDF ausente o desactualizado: '+str(pdf))
    doc=fitz.open(pdf);thumbs=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1,1));pix.save(str(dest/(file.stem+f'_p{i+1:02}.png')))
        img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);img.thumbnail((400,550))
        tile=Image.new('RGB',(420,585),'#ddd');tile.paste(img,(10,25));ImageDraw.Draw(tile).text((10,5),f'Página {i+1}',fill='black');thumbs.append(tile)
    sheet=Image.new('RGB',(1260,585*((len(thumbs)+2)//3)),'white')
    for i,img in enumerate(thumbs):sheet.paste(img,((i%3)*420,(i//3)*585))
    sheet.save(dest/(file.stem+'_contacto.png'));records.append({'archivo':str(pdf),'paginas':len(doc)})
(dest/'render-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
