import flet as ft
import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyAd6Aw-9lhIr2FLFeeM-x2cn_6QJ5Z8OGg",
  'authDomain': "flashcards-f3348.firebaseapp.com",
  'projectId': "flashcards-f3348",
  'storageBucket': "flashcards-f3348.firebasestorage.app",
  'databaseURL': "https:flashcards.firebaseio.com",
  'messagingSenderId': "127324130613",
  'appId': "1:127324130613:web:6fe76a0a2d1ceb3b42507c",
  'measurementId': "G-5RVMDT9WWF"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def main(page: ft.Page):
    page.title = 'Flashcards'
    page.window.width = 830
    page.window.height = 800
    page.bgcolor = 'dark'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'

    # Variáveis para os controles
    email_login = ft.TextField(
        label='Email', 
        text_size=26, 
        width=600, 
        border_color='white'
    )
    
    senha_login = ft.TextField(
        label='Senha', 
        text_size=26, 
        width=600, 
        password=True, 
        can_reveal_password=True, 
        border_color='white'
    )
    
    email_registro = ft.TextField(
        label='Email', 
        text_size=26, 
        width=600, 
        border_color='white'
    )
    
    senha_registro = ft.TextField(
        label='Senha', 
        text_size=26, 
        width=600, 
        password=True, 
        can_reveal_password=True, 
        border_color='white'
    )
    
    confirmar_senha = ft.TextField(
        label='Confirmar Senha', 
        text_size=26, 
        width=600, 
        password=True, 
        can_reveal_password=True, 
        border_color='white'
    )

    def route_change(e):
        page.views.clear()
        
        # Tela de Login
        if page.route == "/" or page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Text(value='Login', size=40),
                        email_login,
                        senha_login,
                        ft.ElevatedButton(
                            text='Entrar', 
                            color='black', 
                            width=200, 
                            bgcolor='white', 
                            on_click=login
                        ),
                        ft.TextButton(
                            text='Criar conta', 
                            on_click=lambda _: page.go("/registro")
                        )
                    ],
                    vertical_alignment='center',
                    horizontal_alignment='center',
                    spacing=20
                )
            )
        
        # Tela de Registro
        elif page.route == "/registro":
            page.views.append(
                ft.View(
                    "/registro",
                    [
                        ft.Text(value='Criar Conta', size=40),
                        email_registro,
                        senha_registro,
                        confirmar_senha,
                        ft.ElevatedButton(
                            text='Registrar', 
                            color='black', 
                            width=200, 
                            bgcolor='white', 
                            on_click=criar_conta
                        ),
                        ft.TextButton(
                            text='Voltar ao Login', 
                            on_click=lambda _: page.go("/login")
                        )
                    ],
                    vertical_alignment='center',
                    horizontal_alignment='center',
                    spacing=20
                )
            )
        
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.go("/login")

    def login(e):
        try:
            auth.sign_in_with_email_and_password(email_login.value, senha_login.value)
            snackbar = ft.SnackBar(
                content=ft.Text("Logado com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )
        except Exception as error:
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro no login: {str(error)}"),
                bgcolor="red",
                duration=3000,
                action="OK"
            )
        
        page.open(snackbar)
        email_login.value = ""
        senha_login.value = ""
        page.update()

    def criar_conta(e):
        if senha_registro.value != confirmar_senha.value:
            snackbar = ft.SnackBar(
                content=ft.Text("As senhas não coincidem!"),
                bgcolor="red",
                duration=3000,
                action="OK"
            )
        else:
            try:
                auth.create_user_with_email_and_password(email_registro.value, senha_registro.value)
                snackbar = ft.SnackBar(
                    content=ft.Text("Conta criada com sucesso!"),
                    bgcolor="green",
                    duration=3000,
                    action="OK"
                )
                # Limpa os campos e volta para o login
                email_registro.value = ""
                senha_registro.value = ""
                confirmar_senha.value = ""
                page.go("/login")
            except Exception as error:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Erro ao criar conta: {str(error)}"),
                    bgcolor="red",
                    duration=3000,
                    action="OK"
                )
        
        page.open(snackbar)
        page.update()

    # Configurar os eventos de navegação
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Iniciar na tela de login
    page.go("/login")

ft.app(main)