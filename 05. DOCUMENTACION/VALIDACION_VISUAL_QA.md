# Verificación WPF y Android sobre QA

## Preparación reproducible

1. Ejecutar `python scripts/IniciarQAVisual.py` y mantenerlo activo. Genera bases únicas y API temporales en 19201/19202. No restablece bases existentes.
2. WPF: `dotnet run --project scripts/WpfQA/WpfQA.csproj -p:CelularBuildRoot=D:/tools/CelularGR09_VisualQA`. El arnés muestra MainWindow y dispara eventos de sus controles reales; acepta solo los diálogos de confirmación esperados. Usar una sesión QA nueva para repetir, pues el crédito activo impide un segundo crédito.
3. Android QA: compilar con `dotnet build "04. CLIMOV/Celulares.Movil/Celulares.Movil.csproj" -p:AndroidSdkDirectory=D:/tools/android-sdk -p:CelularBuildRoot=D:/tools/CelularGR09_MovilQA -p:CelularesApiUrl=http://10.0.2.2:19202/ -p:EmbedAssembliesIntoApk=true`. Instalar el APK firmado en el emulador.

La propiedad MSBuild CelularesApiUrl se guarda como metadato de compilación. Sin ella se conserva el destino normal 10.0.2.2:19102. No se guarda una dirección QA en preferencias de usuario.

## WPF: aprobado

10 comprobaciones de controles/eventos reales: catálogo cargado, alta, edición, desactivación, venta en efectivo, total 261, crédito y amortización, búsqueda por cédula, apertura de factura seleccionada y saldo final cero en la tabla.

La consulta HTTP posterior confirma factura 2 APROBADA, comprador Ana WPF, precio/total 450, descuento cero, crédito 1 y tres cuotas. Evidencia detallada: EVIDENCIA_WPF_QA.json.

Esta automatización no es una inspección visual exhaustiva ni prueba accesibilidad por teclado/ratón.

## Android: aprobado

Nueve recorridos comprobados por ADB en emulator-5554: catálogo, alta, edición, desactivación, efectivo, crédito nuevo, búsqueda, reapertura y amortización con saldo final cero. Factura 3: precio 450, descuento 189, total 261. Factura 4: crédito aprobado por 450, tres cuotas, pagos 154,14 / 154,14 / 154,15. La última absorbe un centavo de redondeo.

Capturas y XML en `evidencias/android_*.png` y `evidencias/android_*.xml`; la captura de amortización se inspeccionó visualmente. Evidencia y huella SHA-256 del APK probado: EVIDENCIA_ANDROID_QA.json. La compilación QA final terminó con cero errores y cero advertencias.

Se observaron fallos transitorios de ADB/UIAutomator; se repitieron las capturas hasta obtener controles actuales, y se contrastaron con la API QA. La utilidad AndroidQA.py descarta archivos XML anteriores y reintenta errores de captura para evitar usar evidencia obsoleta.

La aplicación conserva estado entre pantallas; para repetir entradas existentes, la utilidad selecciona todo el campo antes de escribir. Las ventas de esta ejecución se realizaron con 1111111111 (efectivo) y 0102030405 (crédito), mientras WPF usó 0304050607.

Al terminar se restauró el APK anterior y se detuvieron únicamente las API temporales. Las bases QA se conservan. No se borraron datos de la aplicación ni bases principales.

### Respaldo

 El APK anterior del emulador fue respaldado fuera del repositorio en D:/tools/CelularGR09_MovilAnterior.apk. No se borraron datos de la aplicación. 
