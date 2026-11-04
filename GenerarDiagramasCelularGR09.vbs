Option Explicit

' =============================================================================
' GenerarDiagramasCelularGR09.vbs
' Genera los modelos PowerDesigner (.oom, .eam) y diagramas PNG oficiales para
' el proyecto Comercializadora de Celulares GR09.
' Ejecutar con cscript de 32 bits (SysWOW64\cscript.exe //nologo).
' =============================================================================

Dim app, fso, host, raiz, destino, perfil, modelo, vistos, textoLog
Dim posicionesIniciales, layoutPendiente

Set fso = CreateObject("Scripting.FileSystemObject")
Set host = Nothing
On Error Resume Next
Execute "Set host = WScript"
On Error GoTo 0

If host Is Nothing Then
    raiz = "C:\Users\usuario01\Documents\GABRIEL MURILLO\arquitectura-de-software\U1\TI.1.1"
Else
    raiz = fso.GetParentFolderName(host.ScriptFullName)
End If
destino = raiz

Dim carpetaProyecto
carpetaProyecto = "TI.1.1. PAO202651_CELULAR_BDDLOCAL_RESTFUL_NRC36884_GR09"
If Not fso.FolderExists(fso.BuildPath(destino, carpetaProyecto)) Then
    Err.Raise vbObjectError + 10, , "No existe la carpeta del proyecto: " & carpetaProyecto
End If

Set app = CreateObject("PowerDesigner.Application")
app.InteractiveMode = 2
textoLog = ""

Set perfil = CreateObject("Scripting.Dictionary")
perfil("id") = "CELULAR_RESTFUL_DOTNET_GR09"
perfil("carpeta") = carpetaProyecto
perfil("lenguaje") = ".NET 10 / C# 14"
perfil("protocolo") = "REST / HTTP / JSON"
perfil("puertoTienda") = "19102"
perfil("puertoBanco") = "19101"

Registrar "Iniciando generacion de diagramas UML para Comercializadora Celulares GR09..."

GenerarTipo "01_CASOS_DE_USO", "CasosUso", "PdOOM.Model", "UseCaseDiagram"
GenerarTipo "02_ACTIVIDAD", "Actividad", "PdOOM.Model", "ActivityDiagram"
GenerarTipo "03_SECUENCIA", "Secuencia", "PdOOM.Model", "SequenceDiagram"
GenerarTipo "04_CLASES", "Clases", "PdOOM.Model", "ClassDiagram"
GenerarTipo "05_ARQUITECTURA", "Arquitectura", "PdEAM.Model", "ApplicationArchitectureDiagram"

' Copiar a 01. UML\PowerDesigner
Dim pdDir, f
pdDir = fso.BuildPath(fso.BuildPath(fso.BuildPath(destino, carpetaProyecto), "01. UML"), "PowerDesigner")
CrearCarpeta pdDir
CopiarDiagramasAPowerDesigner

Dim archivoLog
Registrar "Generados modelos PowerDesigner y diagramas PNG de Comercializadora Celulares GR09."
Set archivoLog = fso.CreateTextFile(fso.BuildPath(destino, "DiagramasCelularesGR09-resultado.log"), True, True)
archivoLog.Write textoLog
archivoLog.Close
Set app = Nothing

' =============================================================================
' FUNCIONES AUXILIARES
' =============================================================================

Sub CrearCarpeta(ruta)
    If fso.FolderExists(ruta) Then Exit Sub
    CrearCarpeta fso.GetParentFolderName(ruta)
    fso.CreateFolder ruta
End Sub

Sub Registrar(texto)
    textoLog = textoLog & texto & vbCrLf
    If host Is Nothing Then
        app.Output texto
    Else
        host.Echo texto
    End If
End Sub

Function Tipo(nombre)
    Dim clase
    Set clase = app.MetaModel.GetMetaClassByPublicName(nombre)
    If clase Is Nothing Then Err.Raise vbObjectError + 12, , "Metaclase no disponible: " & nombre
    Tipo = clase.Kind
End Function

Function CodigoTecnico(texto)
    Dim i, caracter, codigo, valor
    codigo = ""
    For i = 1 To Len(texto)
        caracter = Mid(texto, i, 1)
        valor = AscW(caracter)
        If (valor >= 48 And valor <= 57) Or (valor >= 65 And valor <= 90) Or (valor >= 97 And valor <= 122) Or caracter = "_" Then
            codigo = codigo & caracter
        Else
            codigo = codigo & "_"
        End If
    Next
    CodigoTecnico = codigo
End Function

Function Clave(objeto)
    Clave = objeto.Code
    If TypeName(objeto) = "ActivityFlow" Then Clave = objeto.Comment
End Function

Sub Nombrar(objeto, codigo, nombre)
    If TypeName(objeto) = "ActivityFlow" Then
        objeto.Comment = CodigoTecnico(codigo)
        objeto.ConditionAlias = nombre
    Else
        objeto.Code = CodigoTecnico(codigo)
        If nombre <> "" Then objeto.Name = nombre
    End If
End Sub

Function Obtener(coleccion, codigo, nombre)
    Dim objeto
    codigo = CodigoTecnico(codigo)
    For Each objeto In coleccion
        If Clave(objeto) = codigo Then
            Nombrar objeto, codigo, nombre
            vistos(codigo) = True
            Set Obtener = objeto
            Exit Function
        End If
    Next
    Set objeto = coleccion.CreateNew()
    Nombrar objeto, codigo, nombre
    vistos(codigo) = True
    Set Obtener = objeto
End Function

Function Diagrama(coleccion, codigo, nombre)
    Dim d
    If coleccion.Count = 1 Then
        Set d = coleccion.Item(0)
        If Left(d.Code, 5) <> "GR09_" Then d.Code = codigo
    End If
    Set Diagrama = Obtener(coleccion, codigo, nombre)
End Function

Function Simbolo(diagrama, objeto, x, y)
    Dim s
    For Each s In diagrama.Symbols
        If TypeName(s) <> "TextSymbol" Then
            If s.Object Is objeto Then
                Set Simbolo = s
                Exit Function
            End If
        End If
    Next
    Set s = diagrama.AttachObject(objeto)
    s.Position = app.NewPoint(x, y)
    Set Simbolo = s
End Function

Sub PosicionarSimbolo(diagrama, objeto, x, y)
    Dim s
    For Each s In diagrama.Symbols
        If TypeName(s) <> "TextSymbol" Then
            If s.Object Is objeto Then
                s.Position = app.NewPoint(x, y)
                Exit Sub
            End If
        End If
    Next
End Sub

Function Nodo(coleccion, codigo, nombre, diagrama, x, y)
    Dim objeto, s
    Set objeto = Obtener(coleccion, "GR09_" & codigo, nombre)
    Set s = Simbolo(diagrama, objeto, x, y)
    Set Nodo = objeto
End Function

Sub Enlace(diagrama, objeto)
    Dim s
    For Each s In diagrama.Symbols
        If TypeName(s) <> "TextSymbol" Then
            If s.Object Is objeto Then Exit Sub
        End If
    Next
    diagrama.AttachLinkObject objeto
End Sub

Sub Vincular(coleccion, codigo, nombre, origen, fin, diagrama)
    Dim vinculo
    Set vinculo = Obtener(coleccion, "GR09_" & codigo, nombre)
    If Not vinculo.Object1 Is origen Then Set vinculo.Object1 = origen
    If Not vinculo.Object2 Is fin Then Set vinculo.Object2 = fin
    Enlace diagrama, vinculo
End Sub

Function NombreArchivoSeguro(texto)
    Dim caracter
    For Each caracter In Array("\", "/", ":", "*", "?", Chr(34), "<", ">", "|")
        texto = Replace(texto, caracter, "_")
    Next
    NombreArchivoSeguro = Trim(texto)
End Function

Sub ExportarImagenes(modeloActual, rutaModelo)
    Dim raizRuta, diagramaActual, rutaImagen
    raizRuta = Left(rutaModelo, InStrRev(rutaModelo, ".") - 1)
    For Each diagramaActual In modeloActual.AllDiagrams
        rutaImagen = raizRuta & "_" & NombreArchivoSeguro(diagramaActual.Name) & ".png"
        diagramaActual.ExportImage rutaImagen
        Registrar "PNG exportado: " & rutaImagen
    Next
End Sub

Sub CopiaRespaldo(ruta, extension)
    Dim base
    base = Left(ruta, InStrRev(ruta, ".") - 1)
    fso.CopyFile ruta, base & extension, True
End Sub

' =============================================================================
' 1. CASOS DE USO
' =============================================================================
Sub CasosUso()
    Dim d, usuario, banco, caso, codigo, nombre, x, y
    Set d = Diagrama(modelo.UseCaseDiagrams, "GR09_CU_Resumen", "CU_Resumen")
    Set usuario = Nodo(modelo.Actors, "CU_ActorUsuario", "Usuario / Cliente", d, -18000, 0)
    Set banco = Nodo(modelo.Actors, "CU_ActorBanco", "BanQuito API", d, 26000, -9000)

    x = 4000
    y = 22000
    Dim codigos, nombres, i
    codigos = Array("Catalogo", "GestionCat", "VentaEfectivo", "VentaCredito", "Factura", "Amortizacion")
    nombres = Array("Consultar catalogo", "Gestionar catalogo (CRUD)", "Registrar venta en efectivo", "Registrar venta a credito", "Consultar factura", "Consultar amortizacion")

    For i = 0 To UBound(codigos)
        codigo = codigos(i)
        nombre = nombres(i)
        Set caso = Nodo(modelo.UseCases, "CU_" & codigo, nombre, d, x, y)
        Vincular modelo.UseCaseAssociations, "CU_Usuario_" & codigo, "", usuario, caso, d
        If codigo = "VentaCredito" Or codigo = "Amortizacion" Then
            Vincular modelo.UseCaseAssociations, "CU_Banco_" & codigo, "", caso, banco, d
        End If
        y = y - 9000
    Next

    d.Comment = "Comercializadora de Celulares GR09. Gestion de catalogo, ventas en efectivo (descuento 42%) y credito directo con BanQuito."
End Sub

' =============================================================================
' 2. ACTIVIDAD
' =============================================================================
Sub FlujoVenta(d)
    Dim inicio, fin, a1, a2, dec, aEf, aCr, aFact
    Set inicio = Nodo(modelo.Starts, "ACT_Inicio", "Inicio", d, 0, 16000)
    Set a1 = Nodo(modelo.Activities, "ACT_SelCel", "Seleccionar celular del catalogo", d, 0, 10000)
    Set a2 = Nodo(modelo.Activities, "ACT_Elegir", "Elegir forma de pago", d, 0, 4000)
    Set dec = Nodo(modelo.Decisions, "ACT_DecPago", "Es credito?", d, 0, -2000)
    Set aEf = Nodo(modelo.Activities, "ACT_Ef", "Aplicar 42% descuento efectivo", d, -16000, -8000)
    Set aCr = Nodo(modelo.Activities, "ACT_Cr", "Consultar elegibilidad en BanQuito", d, 16000, -8000)
    Set aFact = Nodo(modelo.Activities, "ACT_Fact", "Generar Factura (ID_OPERACION)", d, 0, -15000)
    Set fin = Nodo(modelo.Ends, "ACT_Fin", "Fin Venta", d, 0, -22000)

    Vincular modelo.Flows, "F_Start_A1", "", inicio, a1, d
    Vincular modelo.Flows, "F_A1_A2", "", a1, a2, d
    Vincular modelo.Flows, "F_A2_Dec", "", a2, dec, d
    Vincular modelo.Flows, "F_Dec_Ef", "Efectivo", dec, aEf, d
    Vincular modelo.Flows, "F_Dec_Cr", "Credito", dec, aCr, d
    Vincular modelo.Flows, "F_Ef_Fact", "", aEf, aFact, d
    Vincular modelo.Flows, "F_Cr_Fact", "", aCr, aFact, d
    Vincular modelo.Flows, "F_Fact_Fin", "", aFact, fin, d
    d.Comment = "Flujo de venta: bifurcacion entre efectivo con 42% descuento o credito directo via BanQuito."
End Sub

Sub Actividades()
    Dim d
    Set d = Diagrama(modelo.ActivityDiagrams, "GR09_DA_Venta", "DA_Venta")
    FlujoVenta d
End Sub

' =============================================================================
' 3. SECUENCIA
' =============================================================================
Sub Mensaje(d, codigo, nombre, origen, fin, numero, retorno)
    Dim m, s, existente
    Set m = Obtener(modelo.Messages, "GR09_" & codigo, nombre)
    If Not m.Sender Is origen Then Set m.Sender = origen
    If Not m.Receiver Is fin Then Set m.Receiver = fin
    If m.SequenceNumber <> CStr(numero) Then m.SequenceNumber = CStr(numero)
    m.ControlFlow = "C"
    If retorno Then m.ControlFlow = "R"
    existente = False
    For Each s In d.Symbols
        If s.Object Is m Then existente = True
    Next
    If Not existente Then
        Set s = d.AttachLinkObject(m)
        s.Position = app.NewPoint(s.Position.X, -numero * 1800)
    End If
End Sub

Sub SecuenciaVenta(d)
    Dim user, view, ctrl, api, serv, bank, db
    Set user = Nodo(modelo.Objects, "SEQ_User", "Cliente", d, -36000, 0)
    Set view = Nodo(modelo.Objects, "SEQ_View", "Vista Cliente MVC", d, -24000, 0)
    Set ctrl = Nodo(modelo.Objects, "SEQ_Ctrl", "Controlador", d, -12000, 0)
    Set api  = Nodo(modelo.Objects, "SEQ_Api",  "Comercializadora.Api", d, 0, 0)
    Set serv = Nodo(modelo.Objects, "SEQ_Serv", "ServicioFacturas", d, 12000, 0)
    Set bank = Nodo(modelo.Objects, "SEQ_Bank", "BanQuito.Api", d, 24000, 0)
    Set db   = Nodo(modelo.Objects, "SEQ_Db",   "SQL Server 2025", d, 36000, 0)

    Mensaje d, "DS_01", "1: Ingresar datos de compra", user, view, 1, False
    Mensaje d, "DS_02", "2: Solicitar venta", view, ctrl, 2, False
    Mensaje d, "DS_03", "3: POST /api/facturas (JSON)", ctrl, api, 3, False
    Mensaje d, "DS_04", "4: CrearFacturaAsync(solicitud)", api, serv, 4, False
    Mensaje d, "DS_05", "5: GET /api/credito/elegibilidad", serv, bank, 5, False
    Mensaje d, "DS_06", "6: 200 OK (Sujeto de credito)", bank, serv, 6, True
    Mensaje d, "DS_07", "7: INSERT INTO FACTURA", serv, db, 7, False
    Mensaje d, "DS_08", "8: Factura persistida", db, serv, 8, True
    Mensaje d, "DS_09", "9: ResultadoFactura DTO", serv, api, 9, True
    Mensaje d, "DS_10", "10: 201 Created (JSON)", api, ctrl, 10, True
    Mensaje d, "DS_11", "11: Mostrar confirmacion y cuotas", ctrl, view, 11, False
    Mensaje d, "DS_12", "12: Presentar factura y amortizacion", view, user, 12, True
    d.Comment = "Secuencia de registro de venta a credito directo con validacion BanQuito e idempotencia."
End Sub

Sub Secuencias()
    Dim d
    Set d = Diagrama(modelo.SequenceDiagrams, "GR09_DS_Venta", "DS_Venta")
    SecuenciaVenta d
End Sub

' =============================================================================
' 4. CLASES
' =============================================================================
Sub Operacion(clase, codigo, nombre, retorno)
    Dim o
    Set o = Obtener(clase.Operations, "GR09_OP_" & codigo, nombre)
    o.ReturnType = retorno
End Sub

Sub Clases()
    Dim d, vista, ctrl, cliHttp, ctrlCel, ctrlFac, servCat, servFac, servBan, reglas, entCel, entFac
    Set d = Diagrama(modelo.ClassDiagrams, "GR09_DC", "Clases del servicio y cliente")

    Set vista   = Nodo(modelo.Classes, "DC_Vista",   "Vistas MVC (Consola/WPF/Web/MAUI)", d, -40000, 8000)
    Set ctrl    = Nodo(modelo.Classes, "DC_Ctrl",    "Controlador Tienda", d, -22000, 8000)
    Set cliHttp = Nodo(modelo.Classes, "DC_CliHttp", "ClienteComercializadora (HTTP)", d, -4000, 8000)

    Set ctrlCel = Nodo(modelo.Classes, "DC_CtrlCel", "CelularesController", d, 14000, 16000)
    Set ctrlFac = Nodo(modelo.Classes, "DC_CtrlFac", "FacturasController",  d, 14000, 0)

    Set servCat = Nodo(modelo.Classes, "DC_ServCat", "ServicioCatalogo", d, 32000, 16000)
    Set servFac = Nodo(modelo.Classes, "DC_ServFac", "ServicioFacturas", d, 32000, 0)
    Set servBan = Nodo(modelo.Classes, "DC_ServBan", "ServicioBanQuito", d, 32000, -16000)

    Set reglas  = Nodo(modelo.Classes, "DC_Reglas",  "ReglasFacturacion", d, 50000, -8000)
    Set entCel  = Nodo(modelo.Classes, "DC_EntCel",  "Celular", d, 50000, 16000)
    Set entFac  = Nodo(modelo.Classes, "DC_EntFac",  "Factura", d, 50000, 4000)

    vista.Stereotype = "boundary"
    ctrl.Stereotype = "control"
    cliHttp.Stereotype = "client"
    ctrlCel.Stereotype = "boundary"
    ctrlFac.Stereotype = "boundary"
    servCat.Stereotype = "service"
    servFac.Stereotype = "service"
    servBan.Stereotype = "adapter"
    reglas.Stereotype = "domain"
    entCel.Stereotype = "entity"
    entFac.Stereotype = "entity"

    Operacion ctrl, "C_Cat", "ObtenerCatalogo", "List<CelularDTO>"
    Operacion ctrl, "C_Venta", "Vender", "ResultadoFactura"
    Operacion cliHttp, "H_Cat", "ObtenerCatalogoAsync", "Task<List<CelularDTO>>"
    Operacion cliHttp, "H_Fac", "RegistrarVentaAsync", "Task<ResultadoFactura>"
    Operacion ctrlCel, "R_GetCel", "Get()", "IActionResult"
    Operacion ctrlFac, "R_PostFac", "Post(solicitud)", "IActionResult"
    Operacion servCat, "S_List", "ListarActivosAsync", "Task<List<Celular>>"
    Operacion servFac, "S_Crea", "CrearFacturaAsync", "Task<ResultadoFactura>"
    Operacion servBan, "B_Eleg", "VerificarElegibilidadAsync", "Task<ElegibilidadDTO>"
    Operacion reglas,  "RG_Desc", "CalcularDescuentoEfectivo", "decimal"

    Vincular modelo.Dependencies, "DEP_V_C", "interaccion", vista, ctrl, d
    Vincular modelo.Dependencies, "DEP_C_H", "usa transporte", ctrl, cliHttp, d
    Vincular modelo.Dependencies, "DEP_H_Cel", "REST Celulares", cliHttp, ctrlCel, d
    Vincular modelo.Dependencies, "DEP_H_Fac", "REST Facturas", cliHttp, ctrlFac, d
    Vincular modelo.Dependencies, "DEP_Cel_SC", "delega catalogo", ctrlCel, servCat, d
    Vincular modelo.Dependencies, "DEP_Fac_SF", "delega facturas", ctrlFac, servFac, d
    Vincular modelo.Dependencies, "DEP_SF_SB", "evalua credito", servFac, servBan, d
    Vincular modelo.Dependencies, "DEP_SF_RG", "aplica reglas", servFac, reglas, d
    Vincular modelo.Dependencies, "DEP_SC_Cel", "gestiona catalogo", servCat, entCel, d
    Vincular modelo.Dependencies, "DEP_SF_Fac", "persiste factura", servFac, entFac, d

    d.Comment = "Diagrama de clases: arquitectura desacoplada en capas MVC con transporte compartido Celulares.Cliente."
End Sub

' =============================================================================
' 5. ARQUITECTURA
' =============================================================================
Sub Arquitectura()
    Dim d, consola, wpf, web, movil, sharedLib, api, dbs, banApi, banDb
    Set d = Diagrama(modelo.ApplicationArchitectureDiagrams, "GR09_ARQ", "Arquitectura Comercializadora")

    Set consola = Nodo(modelo.EnterpriseApplications, "ARQ_Consola", "Cliente Consola (.NET 10)", d, -42000, 18000)
    Set wpf     = Nodo(modelo.EnterpriseApplications, "ARQ_Wpf",     "Cliente Escritorio (WPF)",   d, -42000, 6000)
    Set web     = Nodo(modelo.EnterpriseApplications, "ARQ_Web",     "Cliente Web (ASP.NET MVC)",  d, -42000, -6000)
    Set movil   = Nodo(modelo.EnterpriseApplications, "ARQ_Movil",   "Cliente Movil (.NET MAUI)",  d, -42000, -18000)

    Set sharedLib = Nodo(modelo.EnterpriseApplications, "ARQ_Shared",  "Celulares.Cliente (Transporte HTTP)", d, -18000, 0)
    Set api       = Nodo(modelo.EnterpriseApplications, "ARQ_Api",     "Comercializadora.Api (REST 19102)", d, 8000, 0)
    Set dbs       = Nodo(modelo.EnterpriseApplications, "ARQ_DbStore", "ComercializadoraCelulares (SQL Server)", d, 34000, 12000)

    Set banApi  = Nodo(modelo.EnterpriseApplications, "ARQ_BanApi",  "BanQuito.Api (REST 19101)", d, 8000, -18000)
    Set banDb   = Nodo(modelo.EnterpriseApplications, "ARQ_BanDb",   "BanQuitoCore (SQL Server)", d, 34000, -18000)

    Vincular modelo.ApplicationLinks, "LNK_Con_Sha", "Usa Consola", consola, sharedLib, d
    Vincular modelo.ApplicationLinks, "LNK_Wpf_Sha", "Usa WPF", wpf, sharedLib, d
    Vincular modelo.ApplicationLinks, "LNK_Web_Sha", "Usa Web", web, sharedLib, d
    Vincular modelo.ApplicationLinks, "LNK_Mov_Sha", "Usa Movil", movil, sharedLib, d

    Vincular modelo.ApplicationLinks, "LNK_Sha_Api", "HTTP / JSON REST", sharedLib, api, d
    Vincular modelo.ApplicationLinks, "LNK_Api_Dbs", "T-SQL / ADO.NET", api, dbs, d
    Vincular modelo.ApplicationLinks, "LNK_Api_Bap", "HTTP / REST (Credito)", api, banApi, d
    Vincular modelo.ApplicationLinks, "LNK_Bap_Bdb", "T-SQL Core", banApi, banDb, d

    d.Comment = "Arquitectura de la Comercializadora de Celulares GR09: 4 clientes consumen API REST 19102 y BanQuito en 19101."
End Sub

' =============================================================================
' CONTROLADOR GENERAL DE GENERACION
' =============================================================================
Sub GenerarTipo(carpeta, nombre, clase, diagramaInicial)
    Dim directorio, ruta, extension, extensionRespaldo, habiaModelo
    directorio = fso.BuildPath(fso.BuildPath(fso.BuildPath(fso.BuildPath(destino, carpetaProyecto), "01. UML"), "03. DIAGRAMAS UML"), carpeta)
    CrearCarpeta directorio

    extension = ".oom"
    extensionRespaldo = ".oob"
    If clase = "PdEAM.Model" Then
        extension = ".eam"
        extensionRespaldo = ".eab"
    End If

    ruta = fso.BuildPath(directorio, "GR09_" & nombre & extension)
    Set vistos = CreateObject("Scripting.Dictionary")
    Set posicionesIniciales = CreateObject("Scripting.Dictionary")

    habiaModelo = fso.FileExists(ruta)
    If habiaModelo Then
        CopiaRespaldo ruta, extensionRespaldo
        Set modelo = app.OpenModel(ruta, 9)
    Else
        Set modelo = app.CreateModel(Tipo(clase), "|Language=Analysis|Diagram=" & diagramaInicial, 9)
    End If

    If modelo Is Nothing Then Err.Raise vbObjectError + 13, , "No se pudo abrir o crear: " & ruta

    modelo.Name = nombre & " - Comercializadora Celulares GR09"
    modelo.Code = "GR09_" & nombre
    modelo.Comment = "Modelo Comercializadora Celulares GR09. REST / HTTP / JSON sobre .NET 10 y SQL Server 2025 Express."

    Select Case nombre
        Case "CasosUso":     CasosUso
        Case "Actividad":    Actividades
        Case "Secuencia":    Secuencias
        Case "Clases":       Clases
        Case "Arquitectura": Arquitectura
    End Select

    modelo.Save ruta
    ExportarImagenes modelo, ruta
    modelo.Close
    Registrar "Guardado exitoso: " & ruta
End Sub

Sub CopiarDiagramasAPowerDesigner()
    Dim umlBase, srcDir, destDir, archivo
    umlBase = fso.BuildPath(fso.BuildPath(destino, carpetaProyecto), "01. UML")
    srcDir  = fso.BuildPath(umlBase, "03. DIAGRAMAS UML")
    destDir = fso.BuildPath(umlBase, "PowerDesigner")

    ' Copiar archivos modelo y diagramas a PowerDesigner/
    If fso.FileExists(fso.BuildPath(srcDir, "01_CASOS_DE_USO\GR09_CasosUso.oom")) Then
        fso.CopyFile fso.BuildPath(srcDir, "01_CASOS_DE_USO\GR09_CasosUso.oom"), fso.BuildPath(destDir, "GR09_CasosUso.oom"), True
        fso.CopyFile fso.BuildPath(srcDir, "01_CASOS_DE_USO\GR09_CasosUso_CU_Resumen.png"), fso.BuildPath(destDir, "GR09_Celular_CasosUso.png"), True
    End If
    If fso.FileExists(fso.BuildPath(srcDir, "02_ACTIVIDAD\GR09_Actividad.oom")) Then
        fso.CopyFile fso.BuildPath(srcDir, "02_ACTIVIDAD\GR09_Actividad.oom"), fso.BuildPath(destDir, "GR09_Actividad.oom"), True
        fso.CopyFile fso.BuildPath(srcDir, "02_ACTIVIDAD\GR09_Actividad_DA_Venta.png"), fso.BuildPath(destDir, "GR09_Celular_Actividad_Venta.png"), True
    End If
    If fso.FileExists(fso.BuildPath(srcDir, "03_SECUENCIA\GR09_Secuencia.oom")) Then
        fso.CopyFile fso.BuildPath(srcDir, "03_SECUENCIA\GR09_Secuencia.oom"), fso.BuildPath(destDir, "GR09_Secuencia.oom"), True
        fso.CopyFile fso.BuildPath(srcDir, "03_SECUENCIA\GR09_Secuencia_DS_Venta.png"), fso.BuildPath(destDir, "GR09_Celular_Secuencia_Venta.png"), True
    End If
    If fso.FileExists(fso.BuildPath(srcDir, "04_CLASES\GR09_Clases.oom")) Then
        fso.CopyFile fso.BuildPath(srcDir, "04_CLASES\GR09_Clases.oom"), fso.BuildPath(destDir, "GR09_Clases.oom"), True
        fso.CopyFile fso.BuildPath(srcDir, "04_CLASES\GR09_Clases_Clases del servicio y cliente.png"), fso.BuildPath(destDir, "GR09_Celular_Clases.png"), True
    End If
    If fso.FileExists(fso.BuildPath(srcDir, "05_ARQUITECTURA\GR09_Arquitectura.eam")) Then
        fso.CopyFile fso.BuildPath(srcDir, "05_ARQUITECTURA\GR09_Arquitectura.eam"), fso.BuildPath(destDir, "GR09_Arquitectura.eam"), True
        fso.CopyFile fso.BuildPath(srcDir, "05_ARQUITECTURA\GR09_Arquitectura_Arquitectura Comercializadora.png"), fso.BuildPath(destDir, "GR09_Celular_Arquitectura.png"), True
    End If
    Registrar "Copiados modelos y PNGs consolidados a 01. UML\PowerDesigner."
End Sub
