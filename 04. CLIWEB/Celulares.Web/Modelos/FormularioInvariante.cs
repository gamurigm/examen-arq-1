using System.Globalization;
using Microsoft.AspNetCore.Mvc.ModelBinding;

namespace Celulares.Web.Modelos;

// Mantiene el punto decimal de input[type=number] sin cambiar el idioma de la UI.
internal sealed class FormularioInvariante : IValueProviderFactory
{
    public async Task CreateValueProviderAsync(ValueProviderFactoryContext context)
    {
        var request = context.ActionContext.HttpContext.Request;
        if (!request.HasFormContentType) return;
        var form = await request.ReadFormAsync(request.HttpContext.RequestAborted);
        context.ValueProviders.Add(new FormValueProvider(BindingSource.Form, form, CultureInfo.InvariantCulture));
    }
}
