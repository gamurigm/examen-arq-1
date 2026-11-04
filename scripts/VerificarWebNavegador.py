"""Ejecutar con las API QA en 19201/19202 y MVC QA en 19203."""
from pathlib import Path
import json, datetime
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'05. DOCUMENTACION/evidencias'; DEST.mkdir(exist_ok=True)
checks=[]
def ok(label):checks.append(label)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},locale='es-EC')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('dialog',lambda d:d.accept())
    page.goto('http://127.0.0.1:19203/');expect(page.locator('.catalog-item')).to_have_count(3)
    page.screenshot(path=str(DEST/'web_catalogo_oscuro.png'),full_page=True);ok('Catálogo en navegador real')
    page.locator('#theme-toggle').click();expect(page.locator('html')).to_have_attribute('data-theme','claro')
    page.screenshot(path=str(DEST/'web_catalogo_claro.png'),full_page=True);ok('Cambio tema por JavaScript')
    page.locator('.admin-form summary').click();page.locator('#nombreCelular').fill('QA navegador');page.locator('#precioCelular').fill('100')
    page.locator('form[action="/Tienda/Guardar"] button[type="submit"]').click()
    expect(page.locator('.catalog-item')).to_have_count(4);ok('Alta catálogo formulario navegador')
    card=page.locator('.catalog-item').filter(has_text='QA navegador');card.locator('.edit').click()
    expect(page.locator('#nombreCelular')).to_have_value('QA navegador');page.locator('#nombreCelular').fill('QA navegador editado')
    page.locator('#precioCelular').fill('125');page.locator('form[action="/Tienda/Guardar"] button[type="submit"]').click()
    card=page.locator('.catalog-item').filter(has_text='QA navegador editado');expect(card).to_have_count(1);ok('Edición catálogo mediante JavaScript')
    card.locator('form[action="/Tienda/Eliminar"] button').click();expect(page.locator('.catalog-item')).to_have_count(3);ok('Desactivación con confirmación')
    for payment,cedula in [('EFECTIVO','1111111111'),('CREDITO_DIRECTO','0304050607')]:
        page.goto('http://127.0.0.1:19203/')
        page.locator('#celularVenta').select_option('1');expect(page.locator('#Venta_PrecioEsperado')).to_have_value('450.00')
        page.locator('#Venta_Cedula').fill(cedula);page.locator('#Venta_NombreCliente').fill('Comprador navegador')
        page.locator('#formaPago').select_option(payment)
        if payment=='CREDITO_DIRECTO':
            expect(page.locator('#numeroCuotas')).to_be_enabled();page.locator('#numeroCuotas').fill('3')
            page.locator('#consultarCredito').click();expect(page.locator('#resultadoCredito')).to_contain_text('Elegible')
            ok('Elegibilidad por fetch y cuotas habilitadas')
        else:
            expect(page.locator('#numeroCuotas')).to_be_disabled();expect(page.locator('#resumenPrecio')).to_contain_text('261')
            ok('Descuento previo y cuotas deshabilitadas en efectivo')
        page.locator('form[action="/Tienda/Vender"] button[type="submit"]').click()
        page.wait_for_url('**/Tienda/Factura/*');expect(page.locator('.state-badge')).to_contain_text('APROBADA')
        page.screenshot(path=str(DEST/('web_'+payment.lower()+'.png')),full_page=True);ok('Factura aprobada '+payment)
        if payment=='CREDITO_DIRECTO':expect(page.locator('table')).to_contain_text('154');ok('Amortización renderizada en navegador')
    page.goto('http://127.0.0.1:19203/');page.locator('#cedulaBusqueda').fill('0304050607');page.locator('form[action="/Tienda/BuscarFacturas"] button').click()
    page.get_by_role('link',name='Ver detalle').click();page.wait_for_url('**/Tienda/Factura/*');ok('Búsqueda y reapertura factura')
    page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:19203/')
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth');ok('Sin desbordamiento horizontal a 390 px')
    page.screenshot(path=str(DEST/'web_responsive.png'),full_page=True)
    assert not errors,errors;ok('Sin excepciones JavaScript')
    browser.close()
(ROOT/'05. DOCUMENTACION/EVIDENCIA_WEB_NAVEGADOR.json').write_text(json.dumps({'fecha':datetime.datetime.now().isoformat(),'casos':checks,'erroresJS':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(checks),'comprobaciones de navegador aprobadas')
