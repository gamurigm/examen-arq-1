# Manual técnico y guía de defensa
## 1. Arquitectura y requisitos
.NET SDK 10.0.401, Docker Desktop con contenedores Linux y SQL Server 2022 Developer en Docker. Las API y los cuatro clientes se ejecutan en el host. WPF requiere Windows; MAUI requiere SDK Android y emulador/dispositivo. La persistencia usa ADO.NET, sin Entity Framework.
Las bases ComercializadoraCelulares y BanQuitoCore son distintas. La tienda consume BanQuito por REST sin compartir ensamblados ni conexión bancaria. SQL queda expuesto solo en 127.0.0.1:19433.
## 2. Preparación y ejecución
Copiar .env.example a .env y definir una contraseña local fuerte. Ejecutar ./PrepararEntorno.ps1 -IniciarApis desde la raíz. El script inicia SQL, espera salud y aplica creación, migración y semillas sin borrar datos existentes. No guardar .env en Git.
BanQuito escucha en 19101, comercializadora en 19102. Web MVC se ejecuta con dotnet run --project "04. CLIWEB/Celulares.Web/Celulares.Web.csproj"; su configuración usa 19103. Consola y WPF aceptan CELULARES_API_URL; web acepta CelularesApiUrl. Configurar ConnectionStrings__BaseDatos para iniciar API manualmente con la contraseña local.
Android normal usa http://10.0.2.2:19102/ en emulador. La propiedad MSBuild CelularesApiUrl permite una compilación QA con otra URL, sin cambiar el destino predeterminado. No usar 127.0.0.1 desde Android para llegar al host.
## 3. Servicios REST
| Aplicación | Método y ruta | Función |
| Banco | GET /api/credito/elegibilidad?cedula=... | Validar sujeto de crédito |
| Banco | GET /api/credito/clientes/{codigo}/monto-maximo | Máximo por cliente |
| Banco | POST /api/creditos | Otorgar y registrar cuotas |
| Banco | GET /api/creditos/{id}/amortizacion | Consultar plan persistido |
| Tienda | GET/POST /api/celulares; PUT/DELETE /api/celulares/{id} | Catálogo sin inventario |
| Tienda | POST /api/facturas | Efectivo o crédito directo |
| Tienda | GET /api/facturas?cedula=... | Historial de comprador |
| Tienda | GET /api/facturas/{id}/amortizacion | Pasarela bancaria |
El otorgamiento recibe CodigoCliente, PrecioTelefono, NumeroCuotas y ReferenciaVenta. Facturación recibe IdOperacion, Cedula, NombreCliente, IdCelular, FormaPago, NumeroCuotas y PrecioEsperado. FormaPago es EFECTIVO o CREDITO_DIRECTO; efectivo no acepta cuotas. Las referencias permiten reintentos sin duplicar operaciones.
## 4. Base de datos
Los scripts están en 03. BDD y 03. BDD/BanQuito. Crear antes de sembrar. Aplicar 03_MigrarImagenes.sql si la base ya existía sin columnas IMAGEN e IMAGEN_TIPO. No resetear las bases principales para demostrar créditos: usar QA.
El banco guarda crédito y amortización en el mismo esquema dbo del Core. El índice único filtrado evita dos créditos activos por cliente. La tienda conserva estado PENDIENTE durante la coordinación remota y marca APROBADA después de recibir crédito válido.
## 5. Pruebas reproducibles
Ejecutar dotnet test "04. SERVIDOR/Pruebas/Comercializadora.Pruebas.csproj" y dotnet test "04. SERVIDOR/BanQuito.Pruebas/BanQuito.Pruebas.csproj".
python scripts/VerificarApiQA.py crea bases QA únicas y prueba 53 condiciones HTTP. python scripts/VerificarClientesQA.py comprueba consola y formularios MVC. python scripts/IniciarQAVisual.py mantiene API QA para WPF y Android; Ctrl+C detiene sus procesos y conserva las bases.
El arnés WPF está en scripts/WpfQA. AndroidQA.py opera controles ADB y captura PNG/XML; RegistrarEvidenciaAndroidQA.py contrasta las capturas con la persistencia. VerificarWebNavegador.py requiere Playwright/Chrome y una web QA en 19203 conectada a 19202. Cada nueva prueba de crédito debe usar bases nuevas o clientes elegibles distintos.
## 6. Formularios y errores
Los campos HTML numéricos usan punto decimal; MVC los interpreta con cultura invariante, sin modificar la presentación monetaria. Se corrigió el rechazo de un precio 450.00 interpretado como 45000. El recorrido de navegador reproduce y protege esta corrección.
Validar plazos 2/19, monto superior, menor masculino, ausencia de depósito, cliente inexistente y crédito activo. Ante una interrupción, consultar/reintentar la misma referencia. No crear otra operación para disimular un estado pendiente.
## 7. Generación documental y diagramas
Las plantillas están en examples; las fuentes actualizadas y el perfil se mantienen en el repositorio. Instalar scripts/requirements-documentacion.txt en un entorno virtual. Generar borradores, renderizarlos y revisar todas las páginas antes de sustituir la entrega. Registrar hashes de fuente, plantilla y salida.
Los VBS de 01. UML requieren PowerDesigner COM con licencia válida. GenerarDiagramasCelulares.vbs recibe raíz de tienda y raíz bancaria; ambas pueden ser la raíz de este repositorio. Conserva modelos completos existentes. GenerarModelosCelulares.ps1 produce MER conceptual, lógico y físico; comparar atributos con SQL y revisar PNG.
La licencia de evaluación de PowerDesigner está vencida en este equipo. La generación intentada quedó bloqueada antes de producir nuevos modelos; se conservaron los existentes. No confundir presencia de script con diagrama bancario ya entregado.
## 8. Guion de defensa
Mostrar arquitectura, casos de uso bancarios y MER. Comprobar 5/5/50 en SQL. Invocar elegibilidad por cédula, máximo por código y otorgamiento por cliente/precio/cuotas. En cada cliente demostrar catálogo, efectivo por 261 para precio 450, crédito nuevo y amortización hasta saldo cero. Explicar la ambigüedad 35%/30% y el centavo de ajuste final.
## 9. Estado real
Los cuatro clientes fueron ejecutados sobre QA. Evidencias: VALIDACION_DOCKER.md, VALIDACION_API_QA.md, VALIDACION_CLIENTES.md, VALIDACION_VISUAL_QA.md y registros EVIDENCIA_*.json. La revisión visual web y JavaScript se completó después de corregir decimales. Los diagramas y su regeneración editable siguen sujetos al bloqueo de licencia.
