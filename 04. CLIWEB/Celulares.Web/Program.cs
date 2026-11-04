using Celulares.Cliente.Controladores;
using Celulares.Cliente.Servicios;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews(options =>
{
    // Los campos numéricos HTML y JavaScript envían decimales con punto.
    var index = options.ValueProviderFactories.ToList().FindIndex(f =>
        f is Microsoft.AspNetCore.Mvc.ModelBinding.FormValueProviderFactory);
    if (index >= 0) options.ValueProviderFactories[index] = new Celulares.Web.Modelos.FormularioInvariante();
});
builder.Services.AddHttpClient<ClienteComercializadora>(cliente =>
{
    cliente.BaseAddress = ClienteComercializadora.Direccion(builder.Configuration["CelularesApiUrl"]);
    cliente.Timeout = TimeSpan.FromSeconds(30);
});
builder.Services.AddTransient<ControladorTienda>();
var app = builder.Build();
app.UseStaticFiles();
app.UseRouting();
app.MapControllerRoute("default", "{controller=Tienda}/{action=Index}/{id?}");
app.Run();
