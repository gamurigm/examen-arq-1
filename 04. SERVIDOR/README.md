# 04. SERVIDOR — Comercializadora y BanQuito

`Comercializadora.Api` administra catálogo y facturación. `Comercializadora.Dominio` contiene la regla de precio en efectivo; `Contratos` contiene modelos de tienda y DTOs del cliente HTTP.

En una venta a crédito, la API persiste la factura pendiente y llama por HTTP a `BanQuito.Api`, incluida aquí como aplicación independiente. Usa `Servicios:BanQuitoUrl` para configurar la URL. La comercializadora no referencia ensamblados bancarios ni accede a su base.

`BanQuito.Dominio` implementa elegibilidad, monto máximo y amortización. `BanQuito.Contratos` define sus DTOs; `BanQuito.Administracion` aplica los scripts de `03. BDD/BanQuito`; `BanQuito.Pruebas` verifica sus reglas. Se copió el módulo de crédito GR09 del proyecto bancario como fuente inicial, sin modificar aquel proyecto ni incorporar el Core completo de EurekaBank.

El banco escucha en `http://127.0.0.1:19101/`; la API de tienda en `http://127.0.0.1:19102/`. Consulta `05. DOCUMENTACION/ManualTecnico.md` para inicializar y ejecutar ambos desde este repositorio.
