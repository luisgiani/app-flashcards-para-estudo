import flet as ft

def main(page: ft.Page):
    page.title = "Projetinho Flashcards"
    page.window.width = 830
    page.window.height = 800
    page.bgcolor = "gray"

    texto = ft.Row(controls=[
        ft.Text(value="Qual é a cor de plano de fundo?", color="white", size= 20, text_align='center')],
        alignment='center'
    )

    digitar = ft.Row(controls=[
        ft.TextField(label="Digite aqui a sua resposta:", text_size=20)],
        alignment='center'
        )
    
    btn = ft.Row(controls= [
        ft.ElevatedButton(text="Responder")],
        alignment='center' 
        )

    page.add(texto,digitar, btn)

ft.app(main)