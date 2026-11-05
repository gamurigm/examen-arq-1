using Celulares.Cliente.Controladores;
using Celulares.Cliente.Servicios;
using Celulares.Contratos;

namespace Celulares.Movil.Controladores;

public sealed class ControladorMovil
{
    private ControladorTienda? tienda;
    private HttpClient? http;
    private SolicitudFactura? pendiente;

    public Uri? Direccion { get; private set; }
    public bool TieneVentaPendiente => pendiente is not null;

    public void Conectar(Uri direccion)
    {
        if (Direccion == direccion && tienda is not null) return;

        http?.Dispose();
        http = new HttpClient { BaseAddress = direccion, Timeout = TimeSpan.FromSeconds(30) };
        tienda = new ControladorTienda(new ClienteComercializadora(http));
        Direccion = direccion;
    }

    public Task<Celular[]> Catalogo() => Tienda().Catalogo();

    public Task<byte[]> DescargarImagen(Celular celular) => Tienda().DescargarImagen(celular);

    public Task<Celular> Guardar(int? id, string nombre, decimal precio) =>
        Tienda().Guardar(id, nombre, precio);

    public Task SubirImagen(int id, Stream datos, string nombre, string tipo) =>
        Tienda().SubirImagen(id, datos, nombre, tipo);

    public Task QuitarImagen(int id) => Tienda().QuitarImagen(id);

    public Task Eliminar(int id) => Tienda().Eliminar(id);

    public Task<EvaluacionCredito> EvaluarCredito(string cedula) => Tienda().EvaluarCredito(cedula);

    public Task<Factura[]> FacturasPorCedula(string cedula) => Tienda().FacturasPorCedula(cedula);

    public async Task<Factura> RegistrarVenta(SolicitudFactura solicitud)
    {
        ValidarReintento(solicitud);

        pendiente ??= solicitud;
        return await EnviarVentaPendiente();
    }

    public void ValidarReintento(SolicitudFactura solicitud)
    {
        if (pendiente is not null && !Igual(pendiente, solicitud))
            throw new InvalidOperationException("Hay una venta pendiente. Reintente con los mismos datos o inicie una nueva venta.");
    }

    public Task<Factura> ReintentarVenta() => EnviarVentaPendiente();

    private async Task<Factura> EnviarVentaPendiente()
    {
        if (pendiente is null)
            throw new InvalidOperationException("No hay una venta pendiente en esta sesión.");

        var factura = await Tienda().Facturar(pendiente);
        pendiente = null;
        return factura;
    }

    public void NuevaVenta() => pendiente = null;

    public Task<Factura> Factura(int id) => Tienda().Factura(id);

    public Task<Cuota[]> Amortizacion(int id) => Tienda().Amortizacion(id);

    private ControladorTienda Tienda() =>
        tienda ?? throw new InvalidOperationException("Conecte primero con la comercializadora.");

    private static bool Igual(SolicitudFactura izquierda, SolicitudFactura derecha) =>
        izquierda.Cedula == derecha.Cedula &&
        izquierda.NombreCliente == derecha.NombreCliente &&
        izquierda.IdCelular == derecha.IdCelular &&
        izquierda.FormaPago == derecha.FormaPago &&
        izquierda.NumeroCuotas == derecha.NumeroCuotas &&
        izquierda.PrecioEsperado == derecha.PrecioEsperado;
}
