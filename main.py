import flet as ft

def main(page: ft.Page):
    page.bgcolor = 'gray'
    page.window.resizable = False
    page.window.width = 730
    page.window.height = 920
    page.title = 'Flashcards'
    page.window.always_on_top = True



ft.app(target=main)