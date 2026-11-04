using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using System.Text.Json;
using System.Net.Http;
using System.IO;

class Entry
{
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr FindWindow(string? cls,string title);
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr hwnd,int msg,IntPtr w,IntPtr l);
    static readonly List<string> checks = new();
    static MainWindowProxy ui = null!;
    [STAThread] static void Main()
    {
        Environment.SetEnvironmentVariable("CELULARES_API_URL","http://127.0.0.1:19202/");
        var app = new Celulares.Escritorio.App(); 
        app.Startup += async (_,_) => {
            try {
                var win=new Celulares.Escritorio.MainWindow(); ui=new(win); win.Show();
                var timer=new DispatcherTimer { Interval=TimeSpan.FromMilliseconds(100) };
                timer.Tick+=(_,_)=> { foreach(var title in new[]{"Confirmar venta","Confirmar desactivación"}) { var h=FindWindow("#32770",title); if(h!=IntPtr.Zero) PostMessage(h,0x111,(IntPtr)6,IntPtr.Zero); } }; timer.Start();
                await Wait(()=>ui.Get<DataGrid>("Catalogo").Items.Count==3,"Catálogo cargado");
                ui.Click("Nuevo celular"); ui.Text("NombreCelular","QA WPF");ui.Text("PrecioCelular","100");ui.Click("Guardar");
                await Wait(()=>ui.Get<DataGrid>("Catalogo").Items.Count==4,"Alta catálogo");
                ui.Text("NombreCelular","QA WPF editado");ui.Text("PrecioCelular","125");ui.Click("Guardar");
                await Wait(()=>ui.Get<TextBlock>("Estado").Text.Contains("guardado",StringComparison.OrdinalIgnoreCase),"Edición catálogo");
                ui.Click("Desactivar"); await Wait(()=>ui.Get<DataGrid>("Catalogo").Items.Count==3,"Desactivación catálogo");
                ui.Text("Cedula","QA-WPF");ui.Text("Comprador","Comprador WPF");ui.Get<ComboBox>("CelularVenta").SelectedIndex=0;
                ui.Get<ComboBox>("FormaPago").SelectedIndex=0;ui.Click("Confirmar venta");
                await Wait(()=>ui.Get<TextBlock>("DetalleFactura").Text.Contains("EFECTIVO"),"Venta efectivo");
                Check(ui.Get<TextBlock>("DetalleFactura").Text.Contains("261"),"Total efectivo 261");
                ui.Click("Nueva venta");ui.Text("Cedula","0304050607");ui.Text("Comprador","Ana WPF");ui.Get<ComboBox>("CelularVenta").SelectedIndex=0;
                ui.Get<ComboBox>("FormaPago").SelectedIndex=1;ui.Text("Cuotas","3");ui.Click("Confirmar venta");
                await Wait(()=>ui.Get<TextBlock>("DetalleFactura").Text.Contains("CREDITO_DIRECTO") && ui.Get<DataGrid>("TablaCuotas").Items.Count==4,"Venta crédito y amortización");
                ui.Text("CedulaBusqueda","0304050607");ui.Click("Buscar facturas");
                await Wait(()=>ui.Get<DataGrid>("FacturasEncontradas").Items.Count==1,"Búsqueda por cédula");
                ui.Get<DataGrid>("FacturasEncontradas").SelectedIndex=0;ui.Click("Abrir factura seleccionada");
                await Wait(()=>ui.Get<TextBlock>("Estado").Text.Contains("consultada"),"Consulta factura seleccionada");
                var rows=ui.Get<DataGrid>("TablaCuotas").Items;
                var last=rows[rows.Count-1]; Check((decimal)last.GetType().GetProperty("Saldo")!.GetValue(last)! == 0m,"Saldo final cero visible en tabla");
                timer.Stop();
                File.WriteAllText("05. DOCUMENTACION/EVIDENCIA_WPF_QA.json",JsonSerializer.Serialize(new {fecha=DateTime.Now,casos=checks,detalle=ui.Get<TextBlock>("DetalleFactura").Text},new JsonSerializerOptions{WriteIndented=true}));
                Console.WriteLine($"WPF: {checks.Count} comprobaciones aprobadas"); win.Close(); app.Shutdown(0);
            } catch(Exception ex) { File.WriteAllText("scripts/WpfQA.error.log",ex.ToString());app.Shutdown(1); }
        };
        app.Run();
    }
    static void Check(bool value,string name) { if(!value) throw new Exception(name);checks.Add(name); }
    static async Task Wait(Func<bool> predicate,string name) { for(int i=0;i<100;i++){if(predicate()){checks.Add(name);return;}await Task.Delay(100);}throw new Exception(name+": tiempo agotado; "+ui.Get<TextBlock>("Estado").Text); }
    class MainWindowProxy(Window window) {
        public T Get<T>(string name) where T:FrameworkElement => (T)window.FindName(name);
        public void Text(string name,string text)=>Get<TextBox>(name).Text=text;
        public void Click(string content) {var button=Desc(window).OfType<Button>().First(x=>x.Content?.ToString()==content);button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));}
        static IEnumerable<DependencyObject> Desc(DependencyObject parent){for(int i=0;i<System.Windows.Media.VisualTreeHelper.GetChildrenCount(parent);i++){var c=System.Windows.Media.VisualTreeHelper.GetChild(parent,i);yield return c;foreach(var d in Desc(c))yield return d;}}
    }
}



