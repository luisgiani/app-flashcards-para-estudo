import flet as ft
import pyrebase
import random

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

# Cores para os baralhos
cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

def main(page: ft.Page):
    page.title = 'Flashcards'
    page.window.width = 830
    page.window.height = 800
    page.bgcolor = 'dark'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'

    # Variáveis de estado
    baralhos_exemplo = [
        {"nome": "Matemática", "quantidade": 45, "proxima_revisao": 5},
        {"nome": "Inglês", "quantidade": 120, "proxima_revisao": 12},
        {"nome": "História", "quantidade": 80, "proxima_revisao": 0},
        {"nome": "Programação", "quantidade": 200, "proxima_revisao": 25},
    ]

    # Controles de Login/Registro


    def mudar_tela(e):
        page.views.clear()
        
        if page.route == '/login':
            page.views.append(
                ft.View('/login',
                        [
                            titulo_login, email_login, senha_login, botao_login, voltar_registro, pular_login
                        ],
                        vertical_alignment='center',
                        horizontal_alignment='center',
                        spacing=20
                )
            )
        elif page.route == '/registro':
            page.views.append(
                ft.View(
                    '/registro',
                    [
                        titulo_registro, email_registro, senha_registro, botao_registrar, voltar_login
                    ],
                    vertical_alignment='center',
                    horizontal_alignment='center',
                    spacing=20
                )
            )
        elif page.route == '/principal':
            page.views.append(criar_tela_principal())
        elif page.route.startswith('/estudo/'):
            nome_baralho = page.route.replace('/estudo/', '')
            page.views.append(criar_tela_estudo(nome_baralho))
        elif page.route.startswith('/baralho/'):
            nome_baralho = page.route.replace('/baralho/', '')
            page.views.append(criar_tela_detalhes_baralho(nome_baralho))

        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = mudar_tela
    page.on_view_pop = view_pop

    def registrar(e):
        try:
            auth.create_user_with_email_and_password(email_registro.value, senha_registro.value)
            snackbar = ft.SnackBar(
                content=ft.Text("Conta criada com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )
            email_registro.value = ""
            senha_registro.value = ""
            page.go('/login')

        except Exception as error:
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=3000,
                action="OK"
            )

        page.open(snackbar)
        page.update()

    def login(e):
        try:
            auth.sign_in_with_email_and_password(email_login.value, senha_login.value)
            snackbar = ft.SnackBar(
                content=ft.Text("Logado com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )
            page.go('/principal')

        except Exception as error:
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=3000,
                action="OK"
            )

        page.open(snackbar)
        email_login.value = ""
        senha_login.value = ""
        page.update()

    # ====== FUNÇÕES DOS BARALHOS ======
    
    def criar_card_baralho(nome, quantidade, cor_primaria, proxima_revisao=0):
        return ft.Container(
            content=ft.Column([
                # Cabeçalho do card
                ft.Container(
                    content=ft.Text(nome, size=18, weight='bold', color='white'),
                    bgcolor=f"{cor_primaria}AA",
                    padding=10,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15),
                    expand=True
                ),
                
                # Informações do baralho
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{quantidade} cards", size=14, color='white70'),
                        ft.Container(height=5),
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, size=16, color='orange'),
                            ft.Text(f"{proxima_revisao} para revisar", size=12, color='orange')
                        ]) if proxima_revisao > 0 else ft.Container()
                    ]),
                    padding=15,
                    expand=2
                ),
                
                # Botões de ação
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW, 
                            icon_color='green', 
                            tooltip="Estudar", 
                            on_click=lambda e, nome=nome: estudar_baralho(nome)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT, 
                            icon_color='blue',
                            tooltip="Editar",
                            on_click=lambda e, nome=nome: editar_baralho(nome)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE, 
                            icon_color='red',
                            tooltip="Excluir",
                            on_click=lambda e, nome=nome: confirmar_exclusao(nome)
                        )
                    ], alignment='space-around'),
                    padding=10
                )
            ]),
            height=200,
            width=180,
            bgcolor=cor_primaria,
            border_radius=15,
            ink=True,
            on_click=lambda e, nome=nome: visualizar_baralho(nome)
        )

    def criar_tela_principal():
        return ft.View(
            '/principal',
            [
                # Cabeçalho
                ft.Container(
                    content=ft.Row([
                        ft.Text('Meus Baralhos', size=32, weight='bold'),
                        ft.IconButton(icon=ft.Icons.PERSON, icon_size=30)
                    ], alignment='space-between'),
                    padding=20
                ),
                
                # Estatísticas rápidas
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(len(baralhos_exemplo)), size=24, weight='bold'),
                                ft.Text('Baralhos', size=14)
                            ], alignment='center', horizontal_alignment='center'),
                            padding=15,
                            bgcolor='#2A2A2A',
                            border_radius=10,
                            expand=1
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(sum(baralho['quantidade'] for baralho in baralhos_exemplo)), size=24, weight='bold'),
                                ft.Text('Cards', size=14)
                            ], alignment='center', horizontal_alignment='center'),
                            padding=15,
                            bgcolor='#2A2A2A',
                            border_radius=10,
                            expand=1
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(sum(baralho['proxima_revisao'] for baralho in baralhos_exemplo)), size=24, weight='bold'),
                                ft.Text('Para revisar', size=14)
                            ], alignment='center', horizontal_alignment='center'),
                            padding=15,
                            bgcolor='#FF6B6B',
                            border_radius=10,
                            expand=1
                        )
                    ]),
                    padding=20
                ),
                
                # Barra de pesquisa
                ft.Container(
                    content=ft.TextField(
                        hint_text="Pesquisar baralhos...",
                        prefix_icon=ft.Icons.SEARCH,
                        border_color='#444',
                        filled=True,
                        fill_color='#2A2A2A'
                    ),
                    padding=ft.padding.symmetric(horizontal=20)
                ),
                
                # Grid de baralhos
                ft.GridView(
                    [
                        # Baralhos existentes
                        *[criar_card_baralho(
                            nome=baralho['nome'],
                            quantidade=baralho['quantidade'],
                            cor_primaria=cores[i % len(cores)],
                            proxima_revisao=baralho['proxima_revisao']
                        ) for i, baralho in enumerate(baralhos_exemplo)],
                        
                        # Card para adicionar novo
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.ADD, size=40, color='white'),
                                ft.Text("Novo Baralho", size=16, color='white')
                            ], alignment='center', horizontal_alignment='center'),
                            height=180,
                            width=180,
                            bgcolor='#2A2A2A',
                            border_radius=15,
                            alignment=ft.alignment.center,
                            ink=True,
                            on_click=abrir_modal_novo_baralho,
                            border=ft.border.all(2, '#444')
                        )
                    ],
                    max_extent=200,
                    spacing=20,
                    run_spacing=20,
                    padding=20,
                    expand=True
                )
            ],
            bgcolor='dark'
        )

    def criar_tela_estudo(nome_baralho):
        card_atual = 0
        mostrando_frente = True
        
        frente_texto = ft.Text("Frente do card", size=24, text_align='center')
        verso_texto = ft.Text("Verso do card", size=20, text_align='center', color='white70', visible=False)
        
        def virar_card(e):
            nonlocal mostrando_frente
            mostrando_frente = not mostrando_frente
            verso_texto.visible = not verso_texto.visible
            page.update()
        
        def proximo_card(e):
            nonlocal card_atual, mostrando_frente
            card_atual += 1
            mostrando_frente = True
            verso_texto.visible = False
            # Aqui você carregaria o próximo card real
            frente_texto.value = f"Frente do card {card_atual + 1}"
            verso_texto.value = f"Verso do card {card_atual + 1}"
            page.update()
        
        card_content = ft.Container(
            content=ft.Column([
                frente_texto,
                ft.Container(height=20),
                verso_texto
            ], alignment='center', horizontal_alignment='center'),
            height=300,
            width=400,
            bgcolor='#2A2A2A',
            border_radius=20,
            alignment=ft.alignment.center,
            ink=True,
            on_click=virar_card
        )
        
        return ft.View(
            f'/estudo/{nome_baralho}',
            [
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go('/principal')),
                        ft.Text(f"Estudando: {nome_baralho}", size=20),
                        ft.Text(f"Card {card_atual + 1}/50", size=16)
                    ], alignment='space-between'),
                    padding=20
                ),
                
                # Card principal
                ft.Container(
                    content=card_content,
                    alignment=ft.alignment.center,
                    expand=True
                ),
                
                # Botões de dificuldade
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton("Difícil", bgcolor='red', color='white'),
                        ft.ElevatedButton("Médio", bgcolor='orange', color='white'),
                        ft.ElevatedButton("Fácil", bgcolor='green', color='white'),
                        ft.ElevatedButton("Próximo", on_click=proximo_card)
                    ], alignment='space-around'),
                    padding=20
                )
            ],
            bgcolor='dark'
        )

    def criar_tela_detalhes_baralho(nome_baralho):
        return ft.View(
            f'/baralho/{nome_baralho}',
            [
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go('/principal')),
                        ft.Text(nome_baralho, size=24, weight='bold'),
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(text="Editar"),
                                ft.PopupMenuItem(text="Exportar"),
                                ft.PopupMenuItem(text="Estatísticas"),
                            ]
                        )
                    ], alignment='space-between'),
                    padding=20
                ),
                
                # Cards de estatísticas
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("85%", size=20, weight='bold', color='green'),
                                ft.Text("Acertos", size=12)
                            ], alignment='center'),
                            padding=15,
                            bgcolor='#2A2A2A',
                            border_radius=10,
                            expand=1
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("2.3", size=20, weight='bold'),
                                ft.Text("Média/dia", size=12)
                            ], alignment='center'),
                            padding=15,
                            bgcolor='#2A2A2A',
                            border_radius=10,
                            expand=1
                        )
                    ]),
                    padding=20
                ),
                
                # Lista de cards
                ft.ListView(
                    [
                        ft.ListTile(
                            title=ft.Text(f"Card {i}"),
                            subtitle=ft.Text("Pergunta do card..."),
                            trailing=ft.IconButton(icon=ft.Icons.EDIT),
                            on_click=lambda e, i=i: editar_card(i)
                        ) for i in range(10)
                    ],
                    expand=True
                ),
                
                # Botão flutuante para adicionar card
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=lambda e: adicionar_card(nome_baralho),
                    bgcolor='blue'
                )
            ],
            bgcolor='dark'
        )

    def abrir_modal_novo_baralho(e):
        nome_baralho_field = ft.TextField(
            label="Nome do Baralho",
            hint_text="Ex: Vocabulário Inglês",
            border_color='white'
        )
        
        cor_selecionada = ft.Text(value=cores[0])  # Cor padrão
        
        def selecionar_cor(cor):
            cor_selecionada.value = cor
            page.update()
        
        def criar_baralho(e):
            if nome_baralho_field.value:
                # Adicionar novo baralho à lista
                novo_baralho = {
                    "nome": nome_baralho_field.value,
                    "quantidade": 0,
                    "proxima_revisao": 0,
                }
                baralhos_exemplo.append(novo_baralho)
                fechar_modal(e)
                page.go('/principal')
        
        def fechar_modal(e):
            page.dialog.open = False
            page.update()
        
        modal = ft.AlertDialog(
            title=ft.Text("Criar Novo Baralho"),
            content=ft.Column([
                nome_baralho_field,
                ft.Text("Cor do baralho:", size=16),
                ft.Row([
                    ft.Container(
                        width=30, height=30, bgcolor=cor, border_radius=15,
                        on_click=lambda e, cor=cor: selecionar_cor(cor)
                    ) for cor in cores
                ])
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_modal),
                ft.ElevatedButton("Criar", on_click=criar_baralho)
            ]
        )
        
        page.dialog = modal
        modal.open = True
        page.update()

    # ====== FUNÇÕES DE AÇÃO DOS BARALHOS ======
    
    def visualizar_baralho(nome_baralho):
        page.go(f'/baralho/{nome_baralho}')

    def estudar_baralho(nome_baralho):
        page.go(f'/estudo/{nome_baralho}')

    def editar_baralho(nome_baralho):
        # Implementar edição do baralho
        print(f"Editando baralho: {nome_baralho}")

    def confirmar_exclusao(nome_baralho):
        # Implementar confirmação de exclusão
        print(f"Excluindo baralho: {nome_baralho}")

    def editar_card(indice):
        # Implementar edição do card
        print(f"Editando card: {indice}")

    def adicionar_card(nome_baralho):
        # Implementar adição de card
        print(f"Adicionando card ao baralho: {nome_baralho}")


    titulo_login = ft.Text(value='Login', size=40)
    titulo_registro = ft.Text(value='Registrar Conta', size=40)

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

    botao_login = ft.ElevatedButton(
        text='Entrar', 
        color='black', 
        width=200, 
        bgcolor='white', 
        on_click=login
    )

    botao_registrar = ft.ElevatedButton(
        text='Registrar', 
        color='black', 
        width=200, 
        bgcolor='white', 
        on_click=registrar
    )

    voltar_registro = ft.TextButton(
        text='Criar conta', 
        on_click=lambda _: page.go('/registro'),
    )

    voltar_login = ft.TextButton(
        text='Voltar ao Login', 
        on_click=lambda _: page.go('/login')
    )
    
    pular_login = ft.TextButton(
        text='Pular Login', 
        on_click=lambda _: page.go('/principal')
    )
    # Iniciar na tela de login
    page.go('/login')

ft.app(main)