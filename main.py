import flet as ft
from datetime import datetime

MATERIALES_BASE = [
    'TEE 3/8"C/ R INT.1/8" BCE', "TEE 3/8\"x 1/4\" BCE", "TUERCA CON ALETAS P/PORTA PAST",
    'TUERCA EXAG.3/8" BRONCE.', "UNION RECTA 3/8 G", 'UNION RECTA 3/8" G x 1/4" G BCE',
    'UNION RECTA 3/8-1/8 G BCE', 'VIROLA 3/8" BRONCE', 'CODO MM 3/8" BRONCE',
    'CODO MM  3/8" x 1/4" BRONCE', 'PICO PORTAPASTI RH 1/4 PLASTIC', 'PLACA 05 BRONCE(COMUN)',
    'KQH RM 1/4 x 8MM (RECTO)', 'KQH RM 1/8" x 8 MM (RECTO)', 'KQL 8 MM (CODO)'
]

PEDIDOS_DB = []

def main(page: ft.Page):
    try:
        page.title = "Pedido de Materiales"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.bgcolor = ft.colors.WHITE

        es_autorizador = True
        usuario_actual = "Ángel"
        carrito = {}
        tab_actual = "materiales"

        badge_text = ft.Text("0", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
        badge_container = ft.Container(
            content=badge_text,
            bgcolor="#1E293B",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            visible=False
        )

        badge_pendientes = ft.Text("0", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
        badge_pend_container = ft.Container(
            content=badge_pendientes,
            bgcolor="#DC2626",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            visible=False
        )

        btn_tab_mat = ft.ElevatedButton("Materiales", expand=True)
        btn_tab_ped = ft.OutlinedButton(
            content=ft.Row(
                [ft.Text("Mi pedido"), badge_container],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5
            ),
            expand=True
        )
        btn_tab_aprob = ft.OutlinedButton(
            content=ft.Row(
                [ft.Text("Autorizaciones"), badge_pend_container],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5
            ),
            expand=True,
            visible=es_autorizador
        )

        txt_busqueda = ft.TextField(
            hint_text="Buscar material...",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            bgcolor=ft.colors.GREY_100
        )

        lista_materiales_view = ft.ListView(expand=True, spacing=10)
        lista_pedido_view = ft.ListView(expand=True, spacing=10)
        lista_aprobaciones_view = ft.ListView(expand=True, spacing=10)

        lbl_resumen_items = ft.Text("0 items seleccionados", size=14, color=ft.colors.GREY_700)
        btn_enviar_pedido = ft.ElevatedButton(
            "Enviar Pedido",
            icon=ft.icons.SEND,
            bgcolor="#0F2942",
            color=ft.colors.WHITE,
            disabled=True
        )

        def actualizar_badges():
            total_items = sum(carrito.values())
            if total_items > 0:
                badge_text.value = str(total_items)
                badge_container.visible = True
                lbl_resumen_items.value = f"{total_items} items seleccionados"
                btn_enviar_pedido.disabled = False
            else:
                badge_container.visible = False
                lbl_resumen_items.value = "0 items seleccionados"
                btn_enviar_pedido.disabled = True

            pendientes = sum(1 for p in PEDIDOS_DB if p["estado"] == "Pendiente")
            if pendientes > 0 and es_autorizador:
                badge_pendientes.value = str(pendientes)
                badge_pend_container.visible = True
            else:
                badge_pend_container.visible = False

            page.update()

        def render_materiales(filtro=""):
            if filtro is None:
                filtro = ""
            lista_materiales_view.controls.clear()
            for mat in MATERIALES_BASE:
                if filtro.lower() in mat.lower():
                    cant = carrito.get(mat, 0)
                    
                    def make_add(m=mat):
                        def handler(e):
                            carrito[m] = carrito.get(m, 0) + 1
                            render_materiales(txt_busqueda.value or "")
                            actualizar_badges()
                        return handler

                    def make_remove(m=mat):
                        def handler(e):
                            if m in carrito:
                                carrito[m] -= 1
                                if carrito[m] <= 0:
                                    del carrito[m]
                                render_materiales(txt_busqueda.value or "")
                                actualizar_badges()
                        return handler

                    card = ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Row([
                                ft.Text(mat, expand=True, weight=ft.FontWeight.W_500, size=13),
                                ft.Row([
                                    ft.IconButton(ft.icons.REMOVE_CIRCLE_OUTLINE, on_click=make_remove(), icon_color=ft.colors.RED_400 if cant > 0 else ft.colors.GREY_400),
                                    ft.Text(str(cant), weight=ft.FontWeight.BOLD, size=15),
                                    ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, on_click=make_add(), icon_color=ft.colors.GREEN_600)
                                ], alignment=ft.MainAxisAlignment.END)
                            ])
                        )
                    )
                    lista_materiales_view.controls.append(card)
            page.update()

        def render_pedido():
            lista_pedido_view.controls.clear()
            if not carrito:
                lista_pedido_view.controls.append(
                    ft.Container(
                        content=ft.Text("El pedido está vacío", color=ft.colors.GREY_500, size=16),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for mat, cant in carrito.items():
                    card = ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Row([
                                ft.Text(mat, expand=True, size=13),
                                ft.Text(f"Cant: {cant}", weight=ft.FontWeight.BOLD, size=14)
                            ])
                        )
                    )
                    lista_pedido_view.controls.append(card)
            page.update()

        def responder_pedido(pedido_id, nuevo_estado):
            def handler(e):
                for p in PEDIDOS_DB:
                    if p["id"] == pedido_id:
                        p["estado"] = nuevo_estado
                        break
                render_aprobaciones()
                actualizar_badges()
            return handler

        def render_aprobaciones():
            lista_aprobaciones_view.controls.clear()
            pendientes = [p for p in PEDIDOS_DB if p["estado"] == "Pendiente"]
            
            if not pendientes:
                lista_aprobaciones_view.controls.append(
                    ft.Container(
                        content=ft.Text("No hay pedidos pendientes de autorización", color=ft.colors.GREY_500, size=14),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for p in pendientes:
                    items_str = ", ".join([f"{mat} (x{cant})" for mat, cant in p["items"].items()])
                    card = ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"Solicitante: {p['usuario']}", weight=ft.FontWeight.BOLD),
                                    ft.Text(p["fecha"], size=11, color=ft.colors.GREY_600)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Materiales: {items_str}", size=12),
                                ft.Row([
                                    ft.ElevatedButton("Rechazar", bgcolor=ft.colors.RED_600, color=ft.colors.WHITE, on_click=responder_pedido(p["id"], "Rechazado")),
                                    ft.ElevatedButton("Aprobar", bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE, on_click=responder_pedido(p["id"], "Aprobado"))
                                ], alignment=ft.MainAxisAlignment.END, spacing=10)
                            ])
                        )
                    )
                    lista_aprobaciones_view.controls.append(card)
            page.update()

        def cambiar_tab(tab_nombre):
            nonlocal tab_actual
            tab_actual = tab_nombre
            
            container_materiales.visible = (tab_nombre == "materiales")
            container_pedido.visible = (tab_nombre == "pedido")
            container_aprobaciones.visible = (tab_nombre == "aprobaciones")

            if tab_nombre == "pedido":
                render_pedido()
            elif tab_nombre == "aprobaciones":
                render_aprobaciones()

            page.update()

        btn_tab_mat.on_click = lambda e: cambiar_tab("materiales")
        btn_tab_ped.on_click = lambda e: cambiar_tab("pedido")
        btn_tab_aprob.on_click = lambda e: cambiar_tab("aprobaciones")

        txt_busqueda.on_change = lambda e: render_materiales(e.control.value or "")

        def enviar_pedido_click(e):
            if not carrito:
                return
            nuevo_pedido = {
                "id": len(PEDIDOS_DB) + 1,
                "usuario": usuario_actual,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "items": dict(carrito),
                "estado": "Pendiente"
            }
            PEDIDOS_DB.append(nuevo_pedido)
            carrito.clear()
            render_materiales()
            actualizar_badges()
            cambiar_tab("materiales")
            page.snack_bar = ft.SnackBar(ft.Text("¡Pedido enviado con éxito!"))
            page.snack_bar.open = True
            page.update()

        btn_enviar_pedido.on_click = enviar_pedido_click

        def cambiar_rol(e):
            nonlocal es_autorizador
            es_autorizador = e.control.value
            btn_tab_aprob.visible = es_autorizador
            if not es_autorizador and tab_actual == "aprobaciones":
                cambiar_tab("materiales")
            actualizar_badges()

        toggle_rol = ft.Row([
            ft.Text("Modo Autorizador:", size=12, color=ft.colors.WHITE),
            ft.Switch(value=es_autorizador, on_change=cambiar_rol, active_color=ft.colors.GREEN_400)
        ], alignment=ft.MainAxisAlignment.END)

        container_materiales = ft.Column([
            txt_busqueda,
            ft.Container(content=lista_materiales_view, expand=True)
        ], visible=True, expand=True)

        container_pedido = ft.Column([
            ft.Container(content=lista_pedido_view, expand=True),
            ft.Divider(),
            lbl_resumen_items,
            btn_enviar_pedido
        ], visible=False, expand=True)

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
                        container_aprobaciones,
                    ]),
                    padding=15, expand=True
                )
            ], expand=True)
        )

        actualizar_vistas = lambda: render_materiales()
        actualizar_vistas()

    except Exception as ex:
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("ERROR AL INICIAR:", color=ft.colors.RED_600, weight=ft.FontWeight.BOLD, size=18),
                    ft.Text(str(ex), color=ft.colors.BLACK, size=14)
                ]),
                padding=20
            )
        )
        page.update()

if __name__ == "__main__":
    ft.app(target=main)