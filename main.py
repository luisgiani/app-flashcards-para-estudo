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
    page.spacing = 20
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'

    def mudar_tela(e):
        page.views.clear()
        if page.route == '/login':
            page.views.append(
                ft.View('/login',
                        [
                        titulo_login, email, senha, botao_login, msg_registro
                        ]
                )
            )
        elif page.route == '/registro':
            page.views.append(
                ft.View(
                    '/registro',
                    [
                        titulo_registro, email, senha, botao_registrar, msg_login
                    ]
                )
            )

        page.update()

    page.on_route_change = mudar_tela

    def login(e):
        try:
            auth.sign_in_with_email_and_password(email.value, senha.value)
            snackbar = ft.SnackBar(
                content=ft.Text("Logado com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )

        except:
            snackbar = ft.SnackBar(
                content=ft.Text("Email e/ou senha incorretos!"),
                bgcolor="red",
                duration=3000,
                action="OK"
            )

        page.open(snackbar)
        email.value = None
        senha.value = None
        page.update()

    def registrar(e):
        pass
        page.update()

    
    titulo_login = ft.Text(
            value='Login', 
            size=40
            )
    titulo_registro = ft.Text(
            value='Registrar Conta', 
            size=40
            )

    email = ft.TextField(
            label='Email', 
            text_size=26, 
            width=600, 
            border_color='white'
            ) 

    senha = ft.TextField(
            label='Senha', 
            text_size=26, 
            width=600, 
            password=True, 
            can_reveal_password= True, 
            border_color='white'
            ) 

    botao_login = ft.ElevatedButton(
            text='Entrar', 
            color='black', 
            width= 200, 
            bgcolor='white', 
            on_click=login
            )

    botao_registrar = ft.ElevatedButton(
            text='Registrar', 
            color='black', 
            width= 200, 
            bgcolor='white', 
            on_click=registrar
            )

    msg_registro = ft.TextButton(
            text='Criar conta', 
            on_click=lambda _: page.go('/registro'),
            )

    msg_login = ft.TextButton(
            text='Voltar ao Login', 
            on_click=lambda _: page.go('/login')
            )

    page.go('/login')

ft.app(main)