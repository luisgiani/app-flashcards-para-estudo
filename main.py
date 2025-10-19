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

    titulo = ft.Text(value='Login', size=40)

    email = ft.TextField(label='Email', text_size=26, width=600, border_color='white', ) 

    senha = ft.TextField(label='Senha', text_size=26, width=600, password=True, can_reveal_password= True, border_color='white') 

    botao = ft.ElevatedButton(text='Entrar', color='black', width= 200, bgcolor='white')

    page.add(titulo, email, senha, botao)

ft.app(main)