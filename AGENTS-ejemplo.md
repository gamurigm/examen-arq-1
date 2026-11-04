# Proyectos TI.1.1 PAO202651 GR09

- Todos los clientes GR09 separan MVC en el código: `modelo`, `vista` y `controlador`; `servicios` contiene adaptadores y comunicación remota. En .NET, conserva las convenciones del framework cuando correspondan, como `Models`, `Views` y `Controllers` en ASP.NET Core.
- En cada servidor GR09, los controladores publican operaciones, los servicios coordinan la lógica y los modelos representan datos. Mantén paquetes/carpetas equivalentes a `controlador`, `modelo` y `servicios`, más `seguridad`, `configuracion` o `excepciones` cuando existan. Una API no necesita una vista dentro del servidor.
- En proyectos de conversión, cada conversor implementa `IConversor<TUnidad>`; el servicio valida, selecciona y delega las fórmulas. Esta regla solo aplica a conversores.
- Conserva puntos de entrada y directorios nativos de cada plataforma. Ordena vistas, modelos, controladores y servicios en las carpetas MVC del proyecto; no mezcles código de interfaz con llamadas SOAP/REST.
- Consulta ERS, contrato y manuales Word del proyecto para fijar nombres y responsabilidades. GR05 y GR69 solo son ejemplos internos de organización: nunca los menciones como referencias en documentos GR09.
- Mantén la documentación Word del proyecto en sus carpetas numeradas. Registra únicamente funciones que existan en el código o requisitos identificados como pendientes.

## Paridad de clientes e identidad visual

- Antes de cambiar un cliente, compara su contrato, modelos, servicios y flujos con sus clientes equivalentes. Iguala reglas y funciones comunes; conserva códigos anteriores como alias cuando haga falta para mantener compatibilidad.
- Mantén en todos los clientes los mismos nombres y significados para magnitudes, unidades, valor, resultado, sesión y errores. Separa presentación, controlador, modelo y transporte según MVC; adapta los tipos al lenguaje y plataforma.
- Mantén una identidad visual coherente entre los clientes del mismo proyecto. Las pantallas equivalentes deben compartir paleta, tipografía, jerarquía, disposición y textos; adapta controles a cada plataforma.
- Adapta la interfaz solo a los tamaños de pantalla y controles nativos. Usa campos de altura estándar, etiquetas claras, contraseña oculta, foco visible y contraste legible.
- Guarda SDKs, herramientas, descargas, paquetes y artefactos configurables en `D:`. Conserva la estructura numerada y los recursos propios de cada plataforma. No uses Docker para pruebas locales de este equipo.
