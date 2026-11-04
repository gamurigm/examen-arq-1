using System.Reflection;
using Microsoft.Maui.Controls.Hosting;
using Microsoft.Maui.Hosting;

namespace Celulares.Movil;

public static class MauiProgram
{
    // La compilación QA puede apuntar a una API aislada sin cambiar el destino normal.
    internal static readonly string DireccionServidor =
        typeof(MauiProgram).Assembly.GetCustomAttributes<System.Reflection.AssemblyMetadataAttribute>()
            .FirstOrDefault(a => a.Key == "CelularesApiUrl")?.Value ?? "http://10.0.2.2:19102/";

    public static MauiApp CreateMauiApp() => MauiApp.CreateBuilder().UseMauiApp<App>().Build();
}
