import flet as ft
from datetime import datetime

MATERIALES_BASE = [
    "TEE 3/8\"C/ R INT.1/8\"BCE", "TEE 3/8\"x 1/4\" BCE", "TUERCA CON ALETAS P/PORTA PAST",
    "TUERCA EXAG.3/8\"  BRONCE.", "UNION RECTA 3/8 G", "UNION RECTA 3/8\" G x 1/4\" G BCE",
    "UNION RECTA 3/8-1/8 G BCE", "VIROLA 3/8\" BRONCE", "CODO MM 3/8\" BRONCE",
    "CODO MM  3/8\" x 1/4\" BRONCE", "PICO PORTAPASTI RH 1/4 PLASTIC", "PLACA 05 BRONCE(COMUN)",
    "KQH RM 1/4 x 8MM (RECTO)", "KQH RM 1/8\" x 8 MM (RECTO)", "KQL 8 MM (CODO)"
]

PEDIDOS_DB = []

def main(page: ft.Page):
    page.title = "Pedido de Materiales"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.colors.WHITE

    es_autorizador = ft.Ref[bool]()
    es_autorizador.current = True

    usuario_actual = "Ángel"
    carrito = {}
    tab_actual = "materiales"

    badge_text = ft.Text("0", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
    badge_container = ft.Container(
        content=badge_text, bgcolor="#1E293B", border_radius=10,
        padding=ft.padding.symmetric(horizontal=8, vertical=2), visible=False
    )

    badge_pendientes = ft.Text("0", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
    badge_pend_container = ft.Container(
        content=badge_pendientes, bgcolor="#DC2626", border_radius=10,
        padding=ft.padding.symmetric(horizontal=8, vertical=2), visible=False
    )

    btn_tab_mat = ft.ElevatedButton("Materiales", expand=True)
    btn_tab_ped = ft.OutlinedButton(
        content=ft.Row([ft.Text("Mi pedido"), badge_container], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        expand=True
    )
    btn_tab_aprob = ft.OutlinedButton(
        content=ft.Row([ft.Text("Aprobaciones"), badge_pend_container], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        expand=True, visible=es_autorizador.current
    )

    solicitante_tf = ft.TextField(label="Solicitante", value=usuario_actual, border_color=ft.colors.BLUE_GREY_200)
    observaciones_tf = ft.TextField(label="Observaciones (opcional)", hint_text="Urgencia, destino, etc.", multiline=True, min_lines=2, border_color=ft.colors.BLUE_GREY_200)

    lista_materiales_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    lista_pedido_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    lista_aprobaciones_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    search_field = ft.TextField(hint_text="Buscar material...", prefix_icon=ft.icons.SEARCH, dense=True)

    def cambiar_estilado_tabs():
        btn_tab_mat.style = ft.ButtonStyle(
            color=ft.colors.WHITE if tab_actual == "materiales" else ft.colors.BLACK,
            bgcolor="#000000" if tab_actual == "materiales" else ft.colors.TRANSPARENT,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        btn_tab_ped.style = ft.ButtonStyle(
            color=ft.colors.WHITE if tab_actual == "pedido" else ft.colors.BLACK,
            bgcolor="#000000" if tab_actual == "pedido" else ft.colors.TRANSPARENT,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        btn_tab_aprob.style = ft.ButtonStyle(
            color=ft.colors.WHITE if tab_actual == "aprobaciones" else ft.colors.BLACK,
            bgcolor="#000000" if tab_actual == "aprobaciones" else ft.colors.TRANSPARENT,
            shape=ft.RoundedRectangleBorder(radius=8)
        )

    def actualizar_vistas():
        cant_distintos = len(carrito)
        if cant_distintos > 0:
            badge_text.value = str(cant_distintos)
            badge_container.visible = True
        else:
            badge_container.visible = False

        pendientes_count = len([p for p in PEDIDOS_DB if p["estado"] == "Pendiente"])
        if pendientes_count > 0:
            badge_pendientes.value = str(pendientes_count)
            badge_pend_container.visible = True
        else:
            badge_pend_container.visible = False

        cambiar_estilado_tabs()
        render_lista_materiales(search_field.value or "")
        render_lista_pedido()
        render_lista_aprobaciones()
        page.update()

    def cambiar_tab(tab):
        nonlocal tab_actual
        tab_actual = tab
        container_materiales.visible = (tab == "materiales")
        container_pedido.visible = (tab == "pedido")
        container_aprobaciones.visible = (tab == "aprobaciones")
        actualizar_vistas()

    btn_tab_mat.on_click = lambda _: cambiar_tab("materiales")
    btn_tab_ped.on_click = lambda _: cambiar_tab("pedido")
    btn_tab_aprob.on_click = lambda _: cambiar_tab("aprobaciones")

    def modificar_cantidad(idx, delta):
        actual = carrito.get(idx, 0)
        nueva = actual + delta
        if nueva <= 0:
            carrito.pop(idx, None)
        else:
            carrito[idx] = nueva
        actualizar_vistas()

    def enviar_pedido_para_autorizacion(e):
        if not carrito:
            return
        nuevo_pedido = {
            "id": len(PEDIDOS_DB) + 1,
            "solicitante": solicitante_tf.value or "Sin Nombre",
            "observaciones": observaciones_tf.value or "",
            "items": {mat_idx: cant for mat_idx, cant in carrito.items()},
            "estado": "Pendiente",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        PEDIDOS_DB.append(nuevo_pedido)
        carrito.clear()
        observaciones_tf.value = ""
        
        page.show_snack_bar(ft.SnackBar(ft.Text("Pedido enviado para autorización."), open=True))
        cambiar_tab("materiales")

    def responder_pedido(pedido_id, nuevo_estado):
        for p in PEDIDOS_DB:
            if p["id"] == pedido_id:
                p["estado"] = nuevo_estado
                break
        page.show_snack_bar(ft.SnackBar(ft.Text(f"Pedido #{pedido_id} marcado como {nuevo_estado}."), open=True))
        actualizar_vistas()

    def render_lista_materiales(query=""):
        lista_materiales_view.controls.clear()
        query_clean = query.lower().strip()

        for idx, mat in enumerate(MATERIALES_BASE):
            if query_clean and query_clean not in mat.lower():
                continue
            codigo = f"MAT-{idx+1:03d}"
            cant = carrito.get(idx, 0)

            if cant == 0:
                accion = ft.ElevatedButton(
                    "Agregar +",
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor="#000000", shape=ft.RoundedRectangleBorder(radius=6)),
                    on_click=lambda e, i=idx: modificar_cantidad(i, 1)
                )
            else:
                accion = ft.Row([
                    ft.IconButton(ft.icons.REMOVE, on_click=lambda e, i=idx: modificar_cantidad(i, -1), icon_size=18),
                    ft.Text(str(cant), weight=ft.FontWeight.BOLD, size=16),
                    ft.IconButton(ft.icons.ADD, on_click=lambda e, i=idx: modificar_cantidad(i, 1), icon_size=18),
                ], alignment=ft.MainAxisAlignment.END, spacing=0)

            lista_materiales_view.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(mat, weight=ft.FontWeight.BOLD, size=14, width=200),
                            ft.Text(codigo, color=ft.colors.GREY_600, size=12)
                        ], expand=True),
                        accion
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10, border=ft.border.all(1, ft.colors.GREY_300), border_radius=8
                )
            )

    def render_lista_pedido():
        lista_pedido_view.controls.clear()
        for idx, cant in carrito.items():
            mat = MATERIALES_BASE[idx]
            lista_pedido_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(mat, weight=ft.FontWeight.BOLD, size=14),
                        ft.Row([
                            ft.TextButton("Quitar", style=ft.ButtonStyle(color=ft.colors.BLUE_GREY_400),
                                          on_click=lambda e, i=idx: modificar_cantidad(i, -cant)),
                            ft.Row([
                                ft.IconButton(ft.icons.REMOVE, on_click=lambda e, i=idx: modificar_cantidad(i, -1), icon_size=18),
                                ft.Text(str(cant), weight=ft.FontWeight.BOLD, size=16),
                                ft.IconButton(ft.icons.ADD, on_click=lambda e, i=idx: modificar_cantidad(i, 1), icon_size=18),
                            ], spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    padding=10, border=ft.border.all(1, ft.colors.GREY_300), border_radius=8
                )
            )

        if carrito:
            lista_pedido_view.controls.append(
                ft.ElevatedButton(
                    "Enviar Pedido para Autorización",
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor="#0F2942", shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45, width=350,
                    on_click=enviar_pedido_para_autorizacion
                )
            )

    def render_lista_aprobaciones():
        lista_aprobaciones_view.controls.clear()
        pedidos_pendientes = [p for p in PEDIDOS_DB if p["estado"] == "Pendiente"]

        if not pedidos_pendientes:
            lista_aprobaciones_view.controls.append(
                ft.Container(content=ft.Text("No hay pedidos pendientes de autorización.", size=14, color=ft.colors.GREY_600), padding=20)
            )
            return

        for ped in pedidos_pendientes:
            resumen_items = []
            for m_idx, cant in ped["items"].items():
                resumen_items.append(ft.Text(f"• {MATERIALES_BASE[m_idx]} x {cant}", size=13))

            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Pedido #{ped['id']} - {ped['solicitante']}", weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(ped["fecha"], size=11, color=ft.colors.GREY_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Obs: {ped['observaciones']}" if ped['observaciones'] else "Sin observaciones", italic=True, size=12),
                    ft.Divider(height=10),
                    ft.Column(resumen_items),
                    ft.Container(height=5),
                    ft.Row([
                        ft.OutlinedButton("Rechazar", style=ft.ButtonStyle(color=ft.colors.RED_600),
                                          on_click=lambda e, pid=ped["id"]: responder_pedido(pid, "Rechazado")),
                        ft.ElevatedButton("Aprobar Pedido", style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor="#16A34A"),
                                           on_click=lambda e, pid=ped["id"]: responder_pedido(pid, "Aprobado")),
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=12, border=ft.border.all(1, ft.colors.BLUE_GREY_200), border_radius=10, bgcolor="#F8FAFC"
            )
            lista_aprobaciones_view.controls.append(card)

    search_field.on_change = lambda e: (render_lista_materiales(e.control.value), page.update())

    def switch_rol(e):
        es_autorizador.current = e.control.value
        btn_tab_aprob.visible = es_autorizador.current
        solicitante_tf.value = "Ángel" if es_autorizador.current else "Operario"
        cambiar_tab("materiales")

    toggle_rol = ft.Row([
        ft.Text("Modo Autorizador (Ángel):", size=12),
        ft.Switch(value=True, on_change=switch_rol)
    ], alignment=ft.MainAxisAlignment.END)

    container_materiales = ft.Column([search_field, lista_materiales_view], expand=True)
    container_pedido = ft.Column([solicitante_tf, observaciones_tf, lista_pedido_view], visible=False, expand=True)
    container_aprobaciones = ft.Column([
        ft.Text("Pedidos Solicitados para Autorizar:", weight=ft.FontWeight.BOLD, size=16),
        lista_aprobaciones_view
    ], visible=False, expand=True)

    header = ft.Container(
        content=ft.Column([
            ft.Text("PEDIDO DE MATERIALES", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD, size=18),
            ft.Text("CCU SANTA FE", color=ft.colors.WHITE, size=14),
            ft.Text("Sistema de Gestión y Autorización", color=ft.colors.WHITE70, size=12)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#0F2942", padding=15, border_radius=12, alignment=ft.alignment.center
    )

    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    toggle_rol,
                    header,
                    ft.Container(height=5),
                    ft.Row([btn_tab_mat, btn_tab_ped, btn_tab_aprob]),
                    ft.Container(height=10),
                    container_materiales,
                    container_pedido,
                    container_aprobaciones
                ]),
                padding=15, expand=True
            )
        ], expand=True)
    )

    actualizar_vistas()
ft.app(target=main)