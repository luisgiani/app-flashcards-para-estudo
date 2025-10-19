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
    page.title = "Projetinho teste"
    page.window.width = 830
    page.window.height = 800
    page.bgcolor = "gray"
    page.spacing = 20
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'

    titulo = ft.Text(
        value="Teste",
        size= 32
    )

    texto =  ft.Text(value="Qual é a cor de plano de fundo?", 
                color="white", 
                size= 20, 
                )

    digitar = ft.TextField(label="Digite aqui a sua resposta:", 
                     text_size=20
                     )

    
    btn = ft.ElevatedButton(
            text="Responder", 
           # on_click= valida_resposta(digitar)
            )

    page.add(titulo, texto, digitar, btn)

ft.app(main)