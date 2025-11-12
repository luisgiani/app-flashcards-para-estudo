import flet as ft
import pyrebase
import mysql.connector

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

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='', 
    database='flashcards'
)
cursor = conexao.cursor()

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
                        titulo_login, email_login, senha_login, botao_login, voltar_registro, pular_login
                        ],
                        vertical_alignment= 'center',
                        horizontal_alignment= 'center'
                )
            )
        elif page.route == '/registro':
            page.views.append(
                ft.View(
                    '/registro',
                    [
                        titulo_registro, usuario_registro, email_registro, senha_registro, botao_registro, voltar_login
                    ],
                    vertical_alignment= 'center',
                    horizontal_alignment= 'center'
                )
            )
        elif page.route == '/principal':
            grid_baralhos.controls.clear()
            listar_baralhos(e)
            page.views.append(
                ft.View(
                    '/principal',
                    [
                        ft.Row(controls=[titulo_principal, ft.Text(f'meu usuário atual é : {usuario_logado}', color='white')]), stats_inicio, pesquisa, grid_baralhos
                    ]
                )
            )
        elif page.route == '/principal/baralho':
            page.views.append(
                ft.View(
                    '/principal/baralho',
                    [
                        ft.Row(controls=[voltar_principal,ft.Text('Visualização do Baralho', weight='bold',size=28)]),ft.Text(titulo_baralho, size=24), ft.Container(content=lista_cards, border=ft.border.all(1,'white'), border_radius=10, padding=5)
                     ]
                )
            )

        usuario_registro.value = ''
        email_login.value = ''
        senha_login.value = ''
        page.update()

    page.on_route_change = mudar_tela

    def registrar(e):
        try:
            cursor.execute('insert into usuarios (nome_usuario, email, senha) values (%s, %s, %s)', (usuario_registro.value, email_registro.value, senha_registro.value))
            auth.create_user_with_email_and_password(email_registro.value, senha_registro.value)
            conexao.commit()
            snackbar = ft.SnackBar(
                content=ft.Text("Conta criada com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )

        except Exception as error:
            print(f"Erro no registro: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration= 10000,
                action="OK"
            )

        page.open(snackbar)
        usuario_registro.value = ''
        email_registro.value = ''
        senha_registro.value = ''
        page.update()

    def login(e):
        try:
            nonlocal usuario_logado
            auth.sign_in_with_email_and_password(email_login.value, senha_login.value)
            cursor.execute('select id_usuario from usuarios where email = %s',(email_login.value,))
            retorno = cursor.fetchone()
            usuario_logado =retorno[0]

            snackbar = ft.SnackBar(
                content=ft.Text("Logado com sucesso!"),
                bgcolor="green",
                duration=3000,
                action="OK"
            )
            page.go('/principal')

        except Exception as error:
            print(f"Erro no processo: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=10000,
                action="OK"
            )

        page.open(snackbar)
        usuario_registro.value = ''
        email_login.value = ''
        senha_login.value = ''
        page.update()

    def atualizar_stats_iniciais(e):
        nonlocal stats_baralho, stats_cards, stats_revisar
        cursor.execute('select count(*) from baralhos where id_usuario = %s', (usuario_logado,))
        retorno = cursor.fetchone()
        stats_baralho.value = retorno[0]

        cursor.execute('select count(*) from flashcards where cod_baralho in (select cod_baralho from baralhos where id_usuario = %s)', (usuario_logado,))
        retorno = cursor.fetchone()
        stats_cards.value = retorno[0]

        #fazer parte de revisão

    def listar_baralhos(e):
        cursor.execute('select * from baralhos where id_usuario = %s order by nome_baralho',(usuario_logado,))
        lista_baralhos = cursor.fetchall()
        grid_baralhos.controls.append(container_novo_baralho)

        for baralho in lista_baralhos:
            container_baralho = ft.Container(
                content= ft.Text(baralho[2], size=18),
                height=200,
                width=200,
                bgcolor='blue',
                border_radius= 30,
                alignment= ft.alignment.center,
                ink=True,
                on_click=visualizar_baralho
                )
            
            container_baralho.data = baralho[0]
            grid_baralhos.controls.append(container_baralho)
        
        atualizar_stats_iniciais(e)
     
        page.update()

    def adicionar_baralho(e):
        try:
            def alerta_sucesso(e):
                insert_novo_baralho(usuario_logado, nome_baralho, desc_baralho)
                
                snackbar = ft.SnackBar(
                    content=ft.Text("Baralho criado com sucesso!"),
                    bgcolor="green",
                    duration=3000,
                    action="OK"
                )
            
                alerta_baralho_novo.open = False
                nome_baralho.value = ''
                desc_baralho.value = ''
                grid_baralhos.controls.clear()
                listar_baralhos(e)
                page.open(snackbar)
                page.update()

            def alerta_cancelado(e):
                alerta_baralho_novo.open = False
                page.update()

            alerta_baralho_novo = ft.AlertDialog(
                title=titulo_add_baralho,
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            nome_baralho,
                            desc_baralho, 
                            ft.Row(
                                controls=[ft.Container(
                                    content=ft.TextButton(
                                        'Criar',
                                        on_click= lambda _:alerta_sucesso(e),
                                    ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1  
                                                        ),
                                    ft.Container(content=ft.TextButton(
                                        'Cancelar',
                                        on_click= lambda _:alerta_cancelado(e),
                                    ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1  
                                    )],
                                )
                            ],
                            alignment= 'center',
                            spacing=15
                    ),
                    height=180,
                    width=400
                )
            )

            page.open(alerta_baralho_novo)

        except Exception as error:
            print(f"Erro no processo: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=10000,
                action="OK"
            )
            page.open(snackbar)

    def insert_novo_baralho(usuario_logado, nome_baralho, desc_baralho):
        cursor.execute('insert into baralhos (id_usuario, nome_baralho, desc_baralho) values (%s, %s, %s)', (usuario_logado, nome_baralho.value, desc_baralho.value))
        conexao.commit()

    def visualizar_baralho(e):
        nonlocal titulo_baralho,cod_baralho_clicado

        cod_baralho_clicado = e.control.data
        cursor.execute('select nome_baralho from baralhos where cod_baralho = %s',(cod_baralho_clicado,))
        retorno = cursor.fetchone()
        titulo_baralho = retorno[0]

        page.go('/principal/baralho')

        listar_cards(e,cod_baralho_clicado)
        
    def listar_cards(e,cod_baralho_clicado):
        lista_cards.controls.clear()
        cursor.execute('select * from flashcards where cod_baralho = %s', (cod_baralho_clicado,))
        lista_flashcards = cursor.fetchall()

        for card in lista_flashcards:
            flashcard = ft.Container(
                content=ft.Text(card[2], size=16),
                ink=True,
                on_click= lambda _: editar_card(e)
            )

            lista_cards.controls.append(flashcard)

        if not lista_flashcards:
            lista_cards.controls.append(
                ft.Text('Nenhum card encontrado neste baralho', size=16, color='white')
            )
        
        page.update()

    def editar_card(e):
        pass

    usuario_logado = 1
    titulo_baralho = ''
    cod_baralho_clicado = ''

    voltar_principal = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda _:page.go('/principal')
    )

    lista_cards = ft.ListView(
            controls=[ft.Text('Cards:')],
            spacing=10
        )

    titulo_add_baralho = ft.Text(
        value='Adicionar um novo baralho:', 
        weight='bold'
        )

    nome_baralho = ft.TextField(
        label='Nome do baralho', 
        text_size=24,
        border_color='white',
        border_radius=15
        )

    desc_baralho = ft.TextField(
        label='Descrição do baralho', 
        text_size=24,
        border_color='white',
        border_radius=15
        )
    
    titulo_login = ft.Text(
            value='Login', 
            size=40
            )
    titulo_registro = ft.Text(
            value='Registrar Conta', 
            size=40
            )

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
            can_reveal_password= True, 
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
            can_reveal_password= True, 
            border_color='white'
            ) 
    
    usuario_registro = ft.TextField(
        label='Nome do usuário',
        text_size=26,
        width=600,
        border_color='white'
        )

    botao_login = ft.ElevatedButton(
            text='Entrar', 
            color='black', 
            width= 200, 
            bgcolor='white', 
            on_click=login
            )

    botao_registro = ft.ElevatedButton(
            text='Registrar', 
            color='black', 
            width= 200, 
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
    
    titulo_principal = ft.Text(
        value='Meus Baralhos', 
        size= 40,
        weight='bold'
    )

    container_novo_baralho = ft.Container(
        content=ft.Icon(name='ADD', size=50),
        height=200,
        width=200,
        bgcolor='2A2A2A',
        border_radius= 30,
        ink=True,
        on_click=adicionar_baralho,
        alignment= ft.alignment.center,
        border= ft.border.all(1, color='white')
    )

    grid_baralhos = ft.GridView(
        controls=[
            container_novo_baralho
        ],
        expand= True,
        max_extent=200
    )

    stats_baralho = ft.Text(
        '0', 
        size=24, 
        weight='bold'
    )
    
    stats_cards = ft.Text(
        '0', 
        size=24, 
        weight='bold'
    )
    
    stats_revisar = ft.Text(
        '0', 
        size=24, 
        weight='bold'
    )

    stats_inicio = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            stats_baralho,
                            ft.Text(
                                'Baralhos', 
                                size=14
                                )
                        ],
                        alignment= 'center',
                        horizontal_alignment='center'
                    ),
                    bgcolor='blue',
                    padding=15,
                    expand= 1,
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            stats_cards,
                            ft.Text(
                                'Cards', 
                                size=14
                                )
                        ],
                        alignment= 'center',
                        horizontal_alignment='center'
                    ),
                    bgcolor='green',
                    padding=15,
                    expand= 1,
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            stats_revisar,
                            ft.Text(
                                'Para Revisar', 
                                size=14
                                )
                        ],
                        alignment= 'center',
                        horizontal_alignment='center'
                    ),
                    bgcolor='red',
                    padding=15,
                    expand= 1,
                    border_radius=10,
                )
            ]
        ),
    )

    pesquisa = ft.Container(
        content=ft.TextField(
                hint_text='Pesquisar Baralhos', 
                prefix_icon=ft.Icons.SEARCH,
                filled=True
                ), 
            border_radius=10
        )
    
    #criar uma aba de planejamento, onde é definido o tempo dos cards a serem revisados
    #na barra lateral vão ter as abas de usuário, planejamento e estudos(baralhos)
    barra_lateral = ft.NavigationRail()


    page.go('/login')

ft.app(main)