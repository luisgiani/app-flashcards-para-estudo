import flet as ft
import pyrebase
import mysql.connector
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
    
    usuario_logado = 1
    titulo_baralho = ''
    descricao_baralho = ''
    cod_baralho_clicado = ''
    cod_card_clicado = ''
    cards_estudo = []
    indice = 0

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
                        ft.Row(controls=[voltar_principal,ft.Text('Visualização do Baralho', weight='bold',size=26)]),
                        ft.Container(content=ft.Row(controls=[ft.Text('Baralho: ', size=28), tela_titulo_baralho, icone_editar_baralho, icone_excluir_baralho], alignment='left',spacing=5), padding= 2),
                        ft.Row(controls=[ft.Container(content=lista_cards, border=ft.border.all(1,'white'), border_radius=10, margin=10, padding=15, expand= True), coluna_visualizar_baralho], expand= True)
                     ]
                )
            )
        elif page.route == '/principal/baralho/iniciar_estudos':
            iniciar_estudo(e)
            page.views.append(
                ft.View(
                    '/principal/baralho/iniciar_estudos',
                    [
                        ft.Row(controls=[
                            voltar_baralho, titulo_iniciar_estudos
                        ]),
                        coluna_estudo
                    ],
                    vertical_alignment='center',
                    horizontal_alignment='center'
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
                    height=200,
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
        nonlocal titulo_baralho,cod_baralho_clicado,descricao_baralho

        cod_baralho_clicado = e.control.data
        cursor.execute('select nome_baralho, desc_baralho from baralhos where cod_baralho = %s',(cod_baralho_clicado,))
        retorno = cursor.fetchone()
        titulo_baralho = retorno[0]
        tela_titulo_baralho.value = titulo_baralho
        descricao_baralho = retorno[1]

        if descricao_baralho:
            container_desc_baralho.content = ft.Text(f'Descrição: \n{descricao_baralho}', size= 18, color='white')
        else:
            container_desc_baralho.content = ft.Text('Descrição: \nNenhuma descrição foi informada para este baralho.', size= 18, color='white')

        page.go('/principal/baralho')

        listar_cards(e,cod_baralho_clicado)
        
    def listar_cards(e,cod_baralho_clicado):
        lista_cards.controls.clear()
        lista_cards.controls.append(container_novo_card)
        cursor.execute('select * from flashcards where cod_baralho = %s', (cod_baralho_clicado,))
        lista_flashcards = cursor.fetchall()

        for card in lista_flashcards:
            flashcard = ft.Container(
                content=ft.Text(card[2], size=16),
                ink=True,
                on_click= editar_card
            )

            flashcard.data = card[0]

            lista_cards.controls.append(flashcard)

        if not lista_flashcards:
            lista_cards.controls.append(
                ft.Text('Nenhum card encontrado neste baralho', size=16, color='white')
            )
        
        page.update()

    def insert_card(cod_baralho_clicado, pergunta_card, resposta_card):
        cursor.execute('insert into flashcards (cod_baralho, pergunta, resposta) values (%s,%s, %s)', (cod_baralho_clicado,pergunta_card.value, resposta_card.value))
        conexao.commit()

    def adicionar_card(e):
        try:
            def alerta_sucesso(e):
                insert_card(cod_baralho_clicado, pergunta_card, resposta_card)
                
                snackbar = ft.SnackBar(
                    content=ft.Text("Flashcard criado com sucesso!"),
                    bgcolor="green",
                    duration=3000,
                    action="OK"
                )
            
                alerta_card_novo.open = False
                pergunta_card.value = ''
                resposta_card.value = ''
                lista_cards.controls.clear()
                listar_cards(e,cod_baralho_clicado)
                page.open(snackbar)
                page.update()

            def alerta_cancelado(e):
                alerta_card_novo.open = False
                page.update()
            
            alerta_card_novo = ft.AlertDialog(
                title=ft.Text('Novo flashcard'),
                content= ft.Container(
                    content=ft.Column(controls=[
                        pergunta_card, 
                        resposta_card, 
                        ft.Row(controls=[
                            ft.Container(content=ft.TextButton(
                                        'Criar',
                                        on_click= lambda _: alerta_sucesso(e)
                                        ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1
                                    ),
                            ft.Container(content=ft.TextButton(
                                        'Cancelar',
                                        on_click= lambda _: alerta_cancelado(e)
                                        ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1
                                    )
                        ])
                    ]),
                    height= 200,
                    width= 400
                ),
            )

            page.open(alerta_card_novo)

        except Exception as error:
            print(f"Erro no processo: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=10000,
                action="OK"
            )
            page.open(snackbar)

        page.update()

    def editar_card(e):
        try:
            nonlocal cod_card_clicado
            cod_card_clicado = e.control.data

            cursor.execute('select pergunta, resposta from flashcards where cod_flashcard = %s', (cod_card_clicado,))
            card_atual = cursor.fetchone()
            
            if card_atual:
                alterar_pergunta_card.value = card_atual[0]
                alterar_resposta_card.value = card_atual[1]
            else:
                alterar_pergunta_card.value = ''
                alterar_resposta_card.value = ''

            def salvar_alteracoes(e):
                try:
                    cursor.execute('update flashcards set pergunta = %s, resposta = %s where cod_flashcard = %s', 
                                (alterar_pergunta_card.value, alterar_resposta_card.value, cod_card_clicado))
                    conexao.commit()
                    
                    snackbar = ft.SnackBar(
                        content=ft.Text("Card atualizado com sucesso!"),
                        bgcolor="green",
                        duration=3000,
                        action="OK"
                    )
                    
                    alerta_card_edicao.open = False
                    lista_cards.controls.clear()
                    listar_cards(e, cod_baralho_clicado)
                    page.open(snackbar)
                    page.update()

                except Exception as error:
                    print(f"Erro ao salvar: {error}")
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"Erro ao salvar: {str(error)}"),
                        bgcolor="red",
                        duration=10000,
                        action="OK"
                    )
                    page.open(snackbar)

            def excluir_card(e):
                try:
                    cursor.execute('delete from flashcards where cod_flashcard = %s', (cod_card_clicado,))
                    conexao.commit()

                    snackbar = ft.SnackBar(
                        content=ft.Text("Card excluído com sucesso!"),
                        bgcolor="green",
                        duration=3000,
                        action="OK"
                    )
                    
                    alerta_card_edicao.open = False
                    lista_cards.controls.clear()
                    listar_cards(e, cod_baralho_clicado)
                    page.open(snackbar)
                    page.update()

                except Exception as error:
                    print(f"Erro ao excluir: {error}")
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"Erro ao excluir: {str(error)}"),
                        bgcolor="red",
                        duration=10000,
                        action="OK"
                    )
                    page.open(snackbar)

            def cancelar_edicao(e):
                alerta_card_edicao.open = False
                page.update()
            
            alerta_card_edicao = ft.AlertDialog(
                title=ft.Text('Editar flashcard'),
                content=ft.Container(
                    content=ft.Column(controls=[
                        alterar_pergunta_card, 
                        alterar_resposta_card, 
                        ft.Row(controls=[
                            ft.Container(content=ft.TextButton(
                                        'Salvar Alterações',
                                        on_click=salvar_alteracoes
                                        ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1
                                    ),
                            ft.Container(content=ft.TextButton(
                                        'Cancelar',
                                        on_click=cancelar_edicao
                                        ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1
                                    ),
                            ft.Container(content=ft.TextButton(
                                        'Excluir card',
                                        on_click=excluir_card
                                        ),
                                    border=ft.border.all(1,'white'),
                                    border_radius=10,
                                    expand=1
                                    ),
                        ])
                    ]),
                    height=200,
                    width=400
                ),
            )

            page.open(alerta_card_edicao)
            page.update()

        except Exception as error:
            print(f"Erro no processo de edição: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=10000,
                action="OK"
            )
            page.open(snackbar)

    def editar_baralho(e):
        try:
            def salvar_alteracoes(e):
                nonlocal descricao_baralho, titulo_baralho
                if alterar_titulo_baralho.value and alterar_desc_baralho.value:
                    cursor.execute('update baralhos set nome_baralho = %s, desc_baralho = %s where cod_baralho = %s',(alterar_titulo_baralho.value,alterar_desc_baralho.value, cod_baralho_clicado))
                    
                    descricao_baralho = alterar_desc_baralho.value
                    container_desc_baralho.content = ft.Text(f'Descrição: \n{descricao_baralho}', size=18, color='white')

                    titulo_baralho = alterar_titulo_baralho.value
                    tela_titulo_baralho.value = titulo_baralho

                elif alterar_titulo_baralho.value and not alterar_desc_baralho.value:
                    cursor.execute('update baralhos set nome_baralho = %s where cod_baralho = %s', (alterar_titulo_baralho.value, cod_baralho_clicado))

                    titulo_baralho = alterar_titulo_baralho.value
                    tela_titulo_baralho.value = titulo_baralho

                elif alterar_desc_baralho.value and not alterar_titulo_baralho.value:
                    cursor.execute('update baralhos set desc_baralho = %s where cod_baralho = %s', (alterar_desc_baralho.value, cod_baralho_clicado))

                    descricao_baralho = alterar_desc_baralho.value
                    container_desc_baralho.content = ft.Text(f'Descrição: \n{descricao_baralho}', size=18, color='white')

                else:
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"Pelo menos um campo deve ser preenchido!"),
                        bgcolor="red",
                        duration=5000,
                        action="OK"
                    )

                    page.open(snackbar)
                    page.update()
                    return
                
                sucesso = ft.SnackBar(
                        content=ft.Text("Baralho atualizado com sucesso!"),
                        bgcolor="green",
                        duration=3000,
                        action="OK"
                    )

                conexao.commit()
                alerta_edicao.open = False
                alterar_titulo_baralho.value = ''
                alterar_desc_baralho.value = ''
                page.open(sucesso)
                page.update()

            def cancelar_edicao(e):
                alerta_edicao.open = False
                page.update()

            alerta_edicao = ft.AlertDialog(
                title=ft.Text('Editar baralho:'),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            alterar_titulo_baralho,
                            alterar_desc_baralho,
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.TextButton(
                                            'Salvar Alterações',
                                            on_click=lambda _: salvar_alteracoes(e)
                                        ),
                                        border=ft.border.all(1,'white'),
                                        border_radius=10,
                                        expand=1
                                    ),
                                    ft.Container(
                                        content=ft.TextButton(
                                            'Cancelar',
                                            on_click=lambda _: cancelar_edicao(e)
                                        ),
                                        border=ft.border.all(1,'white'),
                                        border_radius=10,
                                        expand=1
                                    )
                                ]
                            )
                        ]
                    ),
                    height=200,
                    width=400
                ))
                    
            page.open(alerta_edicao)

        except Exception as error:
            print(f"Erro no processo: {error}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro: {str(error)}"),
                bgcolor="red",
                duration=10000,
                action="OK"
            )
            page.open(snackbar)

        page.update()

    def excluir_baralho(e):
        def delete_baralho(e):
            try:
                cursor.execute('delete from flashcards where cod_baralho = %s', (cod_baralho_clicado,))
                cursor.execute('delete from baralhos where cod_baralho = %s', (cod_baralho_clicado,))
                conexao.commit()

                snackbar = ft.SnackBar(
                    content=ft.Text(f"Baralho Excluído Com Sucesso"),
                    bgcolor="green",
                    duration=3000,
                    action="OK"
                )

                page.go('/principal')
                page.open(snackbar)

            except Exception as error:
                print(f"Erro no processo: {error}")
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Erro: {str(error)}"),
                    bgcolor="red",
                    duration=10000,
                    action="OK"
                )
                page.open(snackbar)

        def cancelar(e):
            alerta_excluir_baralho.open = False
            page.update()

        alerta_excluir_baralho = ft.AlertDialog(
            title= ft.Text('Deseja excluir o baralho?\n(Essa ação não pode ser desfeita.)', size= 24, color='white', weight='bold'),
            content= ft.Container(
                content=ft.Column(
                    controls=[
                        ft.TextButton(text='Confirmar Exclusão', on_click=lambda _: delete_baralho(e)),
                        ft.TextButton(text='Cancelar', on_click=lambda _: cancelar(e))
                    ]
                ),
                height = 80,
                width= 300
            )
        )

        page.open(alerta_excluir_baralho)
        page.update()

    def iniciar_estudo(e):
        def limpar_variaveis(e):
            nonlocal indice
            indice = 0
            coluna_estudo.controls.clear()

        def puxar_cards(e):
            nonlocal cards_estudo
            cursor.execute('select pergunta, resposta from flashcards where cod_baralho = %s', (cod_baralho_clicado,))
            cards_estudo = cursor.fetchall()
            random.shuffle(cards_estudo)

        def finalizar_estudo(e):
            coluna_estudo.controls.clear()
            coluna_estudo.controls.append(ft.Text("Estudo concluído!", size=24, color='white'))
            coluna_estudo.controls.append(botao_finalizar_estudo)
            page.update()

        def exibir_card(e):
            nonlocal indice

            if indice >= len(cards_estudo):
                finalizar_estudo(e)
                return

            coluna_estudo.controls.clear()
            texto_resposta.visible = False

            numero_pergunta = indice + 1
            texto_resposta.value = cards_estudo[indice][1]

            container_pergunta = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f'Pergunta {numero_pergunta}', size=28, color='white'),
                        ft.Text(cards_estudo[indice][0], size=26, color='white', text_align='center')
                    ]
                ),
                border_radius=10,
                border=ft.border.all(1,'white'),
                margin=10,
                padding=10
            )
            
            container_resposta = ft.Container(
                content=texto_resposta,
                border_radius= 10,
                border=ft.border.all(1,'white'),
                margin=10,
                padding=10
            )

            coluna_estudo.controls.append(container_pergunta)
            coluna_estudo.controls.append(container_resposta)
            coluna_estudo.controls.append(botao_resposta)
            coluna_estudo.controls.append(botao_proximo_card)

            indice += 1
            page.update()      

        botao_proximo_card = ft.ElevatedButton(
            "Próxima Pergunta",
            on_click=exibir_card
            )          

        limpar_variaveis(e)
        puxar_cards(e)
        exibir_card(e)

    def mostrar_resposta(e):
        texto_resposta.visible = not texto_resposta.visible
        page.update()

    alterar_pergunta_card = ft.TextField(
        label='Alterar pergunta do card (Preencha os campos que deseja alterar)',
        text_size=24,
        border_color='white',
        border_radius=15  
    )

    alterar_resposta_card = ft.TextField(
        label='Alterar resposta do card (Preencha os campos que deseja alterar)',
        text_size=24,
        border_color='white',
        border_radius=15  
    )

    botao_finalizar_estudo = ft.TextButton(
        "Finalizar Estudo", 
        on_click=lambda _: page.go('/principal/baralho')
    )

    tela_titulo_baralho = ft.Text(
        titulo_baralho, 
        size=28
        )

    botao_resposta = ft.ElevatedButton(
        "Mostrar/Ocultar Resposta", 
        on_click=mostrar_resposta
        )
    
    texto_resposta = ft.Text(
        "", 
        size=24, 
        color='white', 
        text_align='center', 
        visible=False
        )

    coluna_estudo = ft.Column(
        controls=[],
        expand=True,
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
    )

    alterar_titulo_baralho = ft.TextField(
        label='Novo título (Preencha os campos que deseja alterar)',
        text_size=24,
        border_color='white',
        border_radius=15  
    )
    
    alterar_desc_baralho = ft.TextField(
        label='Nova descrição (Preencha os campos que deseja alterar)',
        text_size=24,
        border_color='white',  
        border_radius=15  
    )

    titulo_iniciar_estudos = ft.Text(
        'Iniciar Estudos', 
        size=24, 
        color='white', 
        text_align='center', 
        weight='bold'
        )

    voltar_baralho = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda _:page.go('/principal/baralho')
    )

    pergunta_card = ft.TextField(
        label='Insira a pergunta deste card',
        text_size=24,
        border_color='white',
        border_radius=15,
    )

    resposta_card = ft.TextField(
        label='Insira a resposta deste card',
        text_size=24,
        border_color='white',
        border_radius=15
    )

    botao_estudar = ft.IconButton(
        icon=ft.Icons.PLAY_CIRCLE,
        bgcolor= 'green',
        icon_color='white',
        scale=1,
        on_click= lambda _: page.go('/principal/baralho/iniciar_estudos')
    )

    container_desc_baralho = ft.Container(
        content='',
        padding=15,
        bgcolor='#2A2A2A',
        border=ft.border.all(1, 'white'),
        border_radius=10,
        margin=10,
        expand=True
    )

    container_iniciar_estudos = ft.Container(
        content=ft.Column(controls=
            [
                ft.Text(
                'Iniciar Estudos', 
                size=24, 
                color='white', 
                text_align='center', 
                weight='bold'
                ), 
                botao_estudar
            ]),
        border=ft.border.all(1,'white'), 
        border_radius=10,
        margin=10, 
        padding=15, 
        expand= True
    )

    coluna_visualizar_baralho = ft.Column(
        controls=[
            container_desc_baralho, container_iniciar_estudos
        ],
        expand=True,
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
    )

    voltar_principal = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda _:page.go('/principal')
    )

    icone_editar_baralho = ft.IconButton(
        icon=ft.Icons.EDIT,
        on_click= editar_baralho
    )

    icone_excluir_baralho = ft.IconButton(
        icon=ft.Icons.DELETE,
        on_click= excluir_baralho
    )

    lista_cards = ft.ListView(
            controls=[],
            spacing=10,
            expand= True
        )

    container_novo_card = ft.Container(
        content=ft.Icon(ft.Icons.ADD),
        ink= True,
        on_click= adicionar_card
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
            on_click=lambda _: page.go('/registro')
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

    page.go('/login')

ft.app(main)