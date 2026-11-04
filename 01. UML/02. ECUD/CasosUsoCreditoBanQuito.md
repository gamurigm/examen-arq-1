# Casos de uso del módulo de crédito BanQuito

Actor principal: sistema de la comercializadora. El comprador proporciona su cédula y el plazo.
El módulo bancario solo expone servicios REST. No implementa ventanillas ni mantenimiento del Core completo.

~~~mermaid
flowchart LR
    A["Comercializadora"] --> V["Verificar sujeto de crédito por cédula"]
    A --> M["Consultar máximo por código de cliente"]
    A --> O["Otorgar crédito"]
    A --> T["Consultar tabla de amortización"]
    O -. incluye .-> V
    O -. incluye .-> M
    O -. incluye .-> G["Generar y registrar amortización"]
~~~

## Caso de uso verificar sujeto de crédito

Identificador: CU-CRE-01.
Objetivo: determinar si el comprador cumple las reglas bancarias.
Disparador: el comprador elige crédito directo y proporciona su cédula.
Precondición: servicio REST y base Core disponibles.

Flujo principal:
1. La comercializadora envía la cédula a GET /api/credito/elegibilidad.
2. El banco localiza al cliente y sus cuentas.
3. Obtiene movimientos de los últimos tres meses y verifica un depósito en el último mes.
4. Comprueba 25 años cumplidos cuando el género sea masculino.
5. Comprueba ausencia de crédito activo.
6. Retorna sujetoCredito, codigoCliente, nombre, motivo y montoMaximo.

Alternativas:
- Cédula vacía o demasiado larga: HTTP 400.
- Cliente inexistente: sujetoCredito=false, codigoCliente=null y motivo legible.
- Regla incumplida: sujetoCredito=false y motivo. No se crea un crédito.
- SQL no disponible: HTTP 503 sin exponer el detalle interno de la conexión.

Postcondición: una decisión de elegibilidad; la consulta no altera datos.
El otorgamiento vuelve a verificar las reglas dentro de una transacción. La consulta previa no garantiza aprobación posterior.

## Caso de uso otorgar crédito

Entradas exigidas: código de cliente, precio del celular y número de cuotas.
La referenciaVenta opcional permite reintentos sin duplicar un crédito.
El banco valida las reglas, el monto máximo y plazo 3..18; registra crédito y cuotas en una transacción serializable.
La tabla incluye fila inicial cero y todas las cuotas. La última absorbe los centavos de redondeo.
Una referencia repetida con otros datos produce conflicto HTTP 409.

