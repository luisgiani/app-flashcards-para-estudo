import flet as ft

def main(page: ft.Page):
    # 1. Função que gerencia TODAS as telas
    def trocar_tela(e):
        page.views.clear()  # Limpa tudo
        
        # TELA 1 - Menu Principal
        if page.route == "/menu":
            page.views.append(
                ft.View(
                    "/menu",
                    [
                        ft.Text("MENU PRINCIPAL", size=30),
                        ft.ElevatedButton(
                            "Ir para Tela 2", 
                            on_click=lambda _: page.go("/tela2")  # Vai para tela 2
                        )
                    ]
                )
            )
        
        # TELA 2 - Segunda Tela  
        elif page.route == "/tela2":
            page.views.append(
                ft.View(
                    "/tela2",
                    [
                        ft.Text("SEGUNDA TELA", size=30),
                        ft.ElevatedButton(
                            "Voltar para Menu",
                            on_click=lambda _: page.go("/menu")  # Volta para menu
                        )
                    ]
                )
            )
        
        page.update()
    
    # 2. Configurar os ouvintes
    page.on_route_change = trocar_tela
    
    # 3. Iniciar na primeira tela
    page.go("/menu")

ft.app(main)