# Imágenes del catálogo de demostración

Fotos descargadas de Pexels el 4 de noviembre de 2026, a 1200 píxeles de ancho. Son ilustrativas: Aurora, Nova y Prisma son nombres del catálogo de prueba y no identifican los dispositivos reales fotografiados. No se cambiaron nombres ni precios del catálogo.

| Archivo | Celular de prueba | Autor y fuente |
|---|---|---|
| aurora.jpg | Celular Aurora 128 GB | [Keifer Costa — Mobile Phone on Black Background](https://www.pexels.com/photo/mobile-phone-on-black-background-11216318/) |
| nova.jpg | Celular Nova 256 GB | [Omar Gerardo — Close-Up of Two Smartphones on White Background](https://www.pexels.com/photo/close-up-of-two-smartphones-on-white-background-30639092/) |
| prisma.jpg | Celular Prisma 64 GB | [Rann Vijay — Close up of Smart Phones](https://www.pexels.com/photo/close-up-of-smart-phones-7952560/) |

Se usan bajo la [licencia Pexels](https://www.pexels.com/legal-pages/license). Los autores conservan los derechos de sus fotos; la licencia del código del proyecto no sustituye esta licencia. No se afirma respaldo de autores o marcas.

`catalogo.json` conserva las URL de origen, descarga, licencia y SHA-256 de cada archivo.

## Cargar en SQL Server mediante la API

Después de inicializar las bases y arrancar la API de comercializadora, ejecutar desde la raíz con PowerShell 7:

```powershell
./scripts/CargarImagenesCatalogo.ps1
```

El script identifica los celulares por nombre, carga los JPEG mediante el endpoint existente y comprueba que los bytes descargados coincidan por SHA-256. La API guarda los bytes y el tipo MIME en `CELULAR.IMAGEN` y `CELULAR.IMAGEN_TIPO` de su base configurada. No requiere volver a descargar las fotos de Internet.

Por defecto conserva cualquier foto existente. Para restaurar explícitamente estas imágenes, ejecutar con `-Reemplazar`. Para otra instancia de API, usar `-ApiUrl http://127.0.0.1:PUERTO/`.
