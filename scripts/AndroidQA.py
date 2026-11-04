"""Utilidades adb para verificar la interfaz Android en emulator-5554."""
import json, pathlib, re, subprocess, sys, time, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
def adb(*args, binary=False):
    return subprocess.check_output(['adb','-s','emulator-5554',*args],text=not binary,encoding=None if binary else 'utf-8',timeout=30)
def nodes():
    for attempt in range(3):
        try:
            adb('shell','rm','-f','/sdcard/celulares-qa.xml')
            adb('shell','uiautomator','dump','/sdcard/celulares-qa.xml')
            result=list(ET.fromstring(adb('shell','cat','/sdcard/celulares-qa.xml')).iter('node'))
            if not any(n.get('package')=='ec.edu.monster.celulares.gr09' for n in result):
                raise RuntimeError('La aplicación Celulares no está en primer plano')
            return result
        except (subprocess.SubprocessError, ET.ParseError, RuntimeError):
            if attempt==2: raise
            time.sleep(1)
def tap_node(n):
    x1,y1,x2,y2=map(int,re.findall(r'\d+',n.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2));time.sleep(.5)
def tap(text):
    n=next(n for n in nodes() if n.get('text')==text or n.get('content-desc')==text)
    tap_node(n)
def fill(placeholder,value):
    n=next(n for n in nodes() if n.get('text')==placeholder and n.get('class')=='android.widget.EditText')
    tap_node(n);adb('shell','input','keyevent','KEYCODE_MOVE_END')
    adb('shell','input','keycombination','113','29');adb('shell','input','keyevent','67')
    adb('shell','input','text',value.replace(' ','%s'));adb('shell','input','keyevent','4')
def scroll():
    adb('shell','input','swipe','540','1850','540','650','500');time.sleep(.5)
def capture(name):
    dest=ROOT/'05. DOCUMENTACION'/'evidencias';dest.mkdir(exist_ok=True)
    (dest/(name+'.png')).write_bytes(adb('exec-out','screencap','-p',binary=True))
    (dest/(name+'.xml')).write_text(ET.tostring(ET.fromstring(adb('shell','cat','/sdcard/celulares-qa.xml')),encoding='unicode'),encoding='utf-8')
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='dump':
        for n in nodes():
            if n.get('text') or n.get('content-desc'): print(n.get('class'),repr(n.get('text')),repr(n.get('content-desc')),n.get('bounds'))
    elif cmd=='tap':tap(sys.argv[2])
    elif cmd=='fill':fill(sys.argv[2],sys.argv[3])
    elif cmd=='scroll':scroll()
    elif cmd=='capture':nodes();capture(sys.argv[2])
