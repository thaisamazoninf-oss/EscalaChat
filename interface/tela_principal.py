import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageDraw, ImageFont

from core.gerador_escala import gerar_escala
from core.regras import DIAS, HORARIOS

from interface.tela_analistas import TelaAnalistas
from core.analistas import GerenciadorAnalistas


class TelaPrincipal:

    def __init__(self, janela):

        self.janela = janela

        self.janela.title(
            "Gerador de Escala de Atendimento"
        )

        self.janela.geometry(
            "1100x650"
        )

        self.janela.minsize(
            950,
            550
        )

        self.escala = None

        self.criar_interface()

    # ======================================================
    # INTERFACE PRINCIPAL
    # ======================================================

    def criar_interface(self):

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        frame_titulo = tk.Frame(
            self.janela
        )

        frame_titulo.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        titulo = tk.Label(
            frame_titulo,
            text="ESCALA DE ATENDIMENTO",
            font=("Arial", 20, "bold")
        )

        titulo.pack()

        """
            subtitulo = tk.Label(
                frame_titulo,
                text="Gerador automático de escala semanal",
                font=("Arial", 10)
            )

            subtitulo.pack(
                pady=(5, 0)
            )
        """

        # --------------------------------------------------
        # BOTÕES
        # --------------------------------------------------

        frame_botoes = tk.Frame(
            self.janela
        )

        frame_botoes.pack(
            pady=10
        )

        # Botão de Analistas
        self.botao_analistas = tk.Button(
            frame_botoes,
            text="Analistas",
            width=18,
            height=2,
            command=self.abrir_analistas
        )

        self.botao_analistas.pack(
            side="left",
            padx=5
        )

        #Botão Gerar Escala
        self.botao_gerar = tk.Button(
            frame_botoes,
            text="Gerar Escala",
            width=18,
            height=2,
            command=self.gerar_escala
        )

        self.botao_gerar.pack(
            side="left",
            padx=5
        )

        #Botão Limpar
        self.botao_limpar = tk.Button(
            frame_botoes,
            text="Limpar",
            width=18,
            height=2,
            command=self.limpar_tabela
        )

        self.botao_limpar.pack(
            side="left",
            padx=5
        )

        #Botão gerar imagem
        self.botao_png = tk.Button(
            frame_botoes,
            text="Gerar Imagem",
            width=18,
            height=2,
            command=self.gerar_png
        )

        self.botao_png.pack(
            side="left",
            padx=5
        )
        # --------------------------------------------------
        # ÁREA DA ESCALA
        # --------------------------------------------------

        frame_escala = tk.LabelFrame(
            self.janela,
            text="Escala semanal",
            font=("Arial", 11, "bold")
        )

        frame_escala.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        # --------------------------------------------------
        # TREEVIEW
        # --------------------------------------------------

        colunas = [
            "horario",
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta"
        ]

        self.tabela = ttk.Treeview(
            frame_escala,
            columns=colunas,
            show="headings"
        )

        # Cabeçalhos

        self.tabela.heading(
            "horario",
            text="Horário"
        )

        self.tabela.heading(
            "segunda",
            text="Segunda"
        )

        self.tabela.heading(
            "terca",
            text="Terça"
        )

        self.tabela.heading(
            "quarta",
            text="Quarta"
        )

        self.tabela.heading(
            "quinta",
            text="Quinta"
        )

        self.tabela.heading(
            "sexta",
            text="Sexta"
        )

        # Largura das colunas

        self.tabela.column(
            "horario",
            width=110,
            anchor="center"
        )

        for coluna in colunas[1:]:

            self.tabela.column(
                coluna,
                width=170,
                anchor="center"
            )

        # Scroll vertical

        scrollbar_y = ttk.Scrollbar(
            frame_escala,
            orient="vertical",
            command=self.tabela.yview
        )

        self.tabela.configure(
            yscrollcommand=scrollbar_y.set
        )

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar_y.pack(
            side="right",
            fill="y"
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status = tk.Label(
            self.janela,
            text="Pronto para gerar a escala.",
            font=("Arial", 10)
        )

        self.status.pack(
            pady=(0, 15)
        )

    # ======================================================
    # GERAR ESCALA
    # ======================================================

    def gerar_escala(self):

        self.status.config(
            text="Gerando escala..."
        )

        self.janela.update_idletasks()

        try:

            # Aqui futuramente vamos buscar os analistas
            # através do GerenciadorAnalistas.

            from core.analistas import GerenciadorAnalistas

            gerenciador = GerenciadorAnalistas()

            analistas = gerenciador.obter_ativos()

            # Gera a escala

            self.escala = gerar_escala(
                analistas,
                DIAS,
                HORARIOS
            )

            if self.escala is None:

                messagebox.showwarning(
                    "Escala",
                    "Não foi possível gerar uma escala "
                    "que atenda todas as regras."
                )

                self.status.config(
                    text="Não foi possível gerar a escala."
                )

                return

            self.mostrar_escala()

            self.status.config(
                text="Escala gerada com sucesso."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Erro ao gerar escala:\n\n{erro}"
            )

            self.status.config(
                text="Erro ao gerar escala."
            )

    # ======================================================
    # MOSTRAR ESCALA
    # ======================================================

    def mostrar_escala(self):

        # Limpa somente os itens da tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # Percorre os horários

        for inicio, fim in HORARIOS:

            horario = (
                f"{inicio.replace(':', 'h')}"
                f"–"
                f"{fim.replace(':', 'h')}"
            )

            valores = [
                horario
            ]

            # Segunda até sexta

            for dia in DIAS:

                nome = self.escala.get(
                    (dia, inicio, fim),
                    ""
                )

                valores.append(
                    nome
                )

            self.tabela.insert(
                "",
                "end",
                values=valores
            )

    # ======================================================
    # LIMPAR TABELA
    # ======================================================

    def limpar_tabela(self):

        for item in self.tabela.get_children():

            self.tabela.delete(
                item
            )

        self.escala = None

        self.status.config(
            text="Tabela limpa."
        )

    # ======================================================
    # GERAR IMAGEM DA ESCALA
    # ======================================================
    def gerar_png(self):

        if not self.escala:
            messagebox.showwarning(
                "Atenção",
                "Gere uma escala antes de criar a imagem."
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar imagem da escala",
            defaultextension=".png",
            filetypes=[
                ("Imagem PNG", "*.png")
            ],
            initialfile="escala.png"
        )

        if not caminho:
            return

        try:
            # -----------------------------------------
            # CONFIGURAÇÕES
            # -----------------------------------------

            largura_horario = 130
            largura_dia = 190

            altura_titulo = 90
            #altura_subtitulo = 40
            altura_cabecalho = 55
            altura_linha = 45
            #altura_rodape = 55

            margem = 30

            largura_tabela = (
                largura_horario +
                (largura_dia * len(DIAS))
            )

            largura_total = (
                largura_tabela +
                (margem * 2)
            )

            altura_total = (
                altura_titulo +
                #altura_subtitulo +
                altura_cabecalho +
                (len(HORARIOS) * altura_linha) +
                # altura_rodape +
                (margem * 2)
            )
            # ==================================================
            # CORES
            # ==================================================

            cor_fundo = "#F4F6F8"
            cor_titulo = "#1F2937"
            cor_cabecalho = "#1F4E78"
            cor_horario = "#DCE6F1"
            cor_linha_1 = "#FFFFFF"
            cor_linha_2 = "#F7F9FB"
            cor_borda = "#CBD5E1"
            cor_texto = "#1F2937"
            #cor_rodape = "#E8EEF4"

            # -----------------------------------------
            # CRIA A IMAGEM
            # -----------------------------------------

            imagem = Image.new(
                "RGB",
                (
                    largura_total,
                    altura_total
                ),
                cor_fundo
            )

            desenho = ImageDraw.Draw(imagem)

            # -----------------------------------------
            # FONTE
            # -----------------------------------------

            try:

                fonte_titulo = ImageFont.truetype(
                    "arial.ttf",
                    28
                )

                """
                fonte_subtitulo = ImageFont.truetype(
                    "arial.ttf",
                    16
                )
                """

                fonte_cabecalho = ImageFont.truetype(
                    "arialbd.ttf",
                    16
                )

                fonte_horario = ImageFont.truetype(
                    "arialbd.ttf",
                    15
                )

                fonte_nome = ImageFont.truetype(
                    "arial.ttf",
                    15
                )

                """
                fonte_rodape = ImageFont.truetype(
                    "arial.ttf",
                    14
                )
                """
            except OSError:

                fonte_titulo = ImageFont.load_default()
                #fonte_subtitulo = ImageFont.load_default()
                fonte_cabecalho = ImageFont.load_default()
                fonte_horario = ImageFont.load_default()
                fonte_nome = ImageFont.load_default()
                #fonte_rodape = ImageFont.load_default()

            # ==================================================
            # FUNÇÃO PARA CENTRALIZAR TEXTO
            # ==================================================

            def texto_centralizado(
                texto,
                caixa, 
                fonte, 
                fill
            ):
                
                x1, y1, x2, y2 = caixa

                bbox = desenho.textbbox(
                    (0, 0),
                    texto,
                    font=fonte
                )

                largura_texto = bbox[2] - bbox[0]
                altura_texto = bbox[3] - bbox[1]

                x = (
                    x1 +
                    ((x2 - x1 - largura_texto) / 2)
                )

                y = (
                    y1 +
                    ((y2 - y1 - altura_texto) / 2) -
                    2
                )

                desenho.text(
                    (x, y),
                    texto,
                    font=fonte,
                    fill=fill
                )
                

            # -----------------------------------------
            # TÍTULO
            # -----------------------------------------

            titulo = "ESCALA DO CHAT"

            texto_centralizado(
                titulo,
                (
                    margem,
                    10,
                    largura_total - margem,
                    altura_titulo
                ),
                fonte_titulo,
                cor_titulo
            )

            # ==================================================
            # SUBTÍTULO
            # ==================================================

            #subtitulo = "Escala semanal de atendimento"
            """
            texto_centralizado(
                subtitulo,
                (
                    margem,
                    altura_titulo,
                    largura_total - margem,
                    altura_titulo + altura_subtitulo
                ),
                fonte_subtitulo,
                cor_texto
            )
            """
            # -----------------------------------------
            # INÍCIO DA TABELA
            # -----------------------------------------
            x_inicial = margem

            y_inicial = (
                altura_titulo
                #+
                #altura_subtitulo
            )

            # -----------------------------------------
            # CABEÇALHO
            # -----------------------------------------

            cabecalhos = [
                "Horário",
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta"
            ]

            larguras = [
                largura_horario
            ] + [
                largura_dia
                for _ in DIAS
            ]

            x = x_inicial

            for indice, cabecalho in enumerate(cabecalhos):

                largura = larguras[indice]

                caixa = (
                        x,
                        y_inicial,
                        x + largura,
                        y_inicial + altura_cabecalho
                )

                desenho.rectangle(
                    caixa,
                    fill=cor_cabecalho,
                    outline=cor_borda
                )

                texto_centralizado(
                    cabecalho,
                    caixa,
                    fonte_cabecalho,
                    "white"
                )

                x += largura
            # -----------------------------------------
            # LINHAS DA ESCALA
            # -----------------------------------------

            y = (
                y_inicial +
                altura_cabecalho
            )

            total_atendimentos = 0

            for indice_horario, (inicio, fim) in enumerate(HORARIOS):

                horario = (
                    f"{inicio.replace(':', 'h')}"
                    f"–"
                    f"{fim.replace(':', 'h')}"
                )

                valores = [
                    horario
                ]

                for dia in DIAS:

                    nome = self.escala.get(
                        (dia, inicio, fim),
                        ""
                    )

                    valores.append(
                        nome
                    )

                    if nome:
                        total_atendimentos += 1

                # ------------------------------
                # Cor da linha
                # ------------------------------

                if indice_horario % 2 == 0:
                    cor_linha = cor_linha_1
                else:
                    cor_linha = cor_linha_2

                x = x_inicial

                # ------------------------------
                # Células
                # ------------------------------

                for indice, valor in enumerate(valores):

                    largura = larguras[indice]

                    caixa = (
                        x,
                        y,
                        x + largura,
                        y + altura_linha
                    )

                    # Cor especial para horário
                    if indice == 0:
                        preenchimento = cor_horario
                        fonte = fonte_horario
                    else:
                        preenchimento = cor_linha
                        fonte = fonte_nome

                    desenho.rectangle(
                        caixa,
                        fill=preenchimento,
                        outline=cor_borda
                    )

                    texto_centralizado(
                        str(valor),
                        caixa,
                        fonte,
                        cor_texto
                    )

                    x += largura

                y += altura_linha

            # ==================================================
            # RODAPÉ
            # ==================================================
            """
            caixa_rodape = (
                margem,
                y + 15,
                largura_total - margem,
                y + 15 + altura_rodape
            )

            desenho.rounded_rectangle(
                caixa_rodape,
                radius=10,
                fill=cor_rodape,
                outline=cor_borda
            )

            texto_rodape = (
                f"Total de atendimentos na semana: "
                f"{total_atendimentos}"
            )

            texto_centralizado(
                texto_rodape,
                caixa_rodape,
                fonte_rodape,
                cor_titulo
            )
            """
            # -----------------------------------------
            # SALVA
            # -----------------------------------------

            imagem.save(
                caminho,
                "PNG"
            )

            messagebox.showinfo(
                "Sucesso",
                "Imagem da escala gerada com sucesso!"
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar a imagem:\n\n{erro}"
            )

    # ======================================================
    # ABRIR TELA DE ANALISTAS
    # ======================================================

    def abrir_analistas(self):

        janela = tk.Toplevel(
            self.janela
        )

        gerenciador = GerenciadorAnalistas()

        TelaAnalistas(
            janela,
            gerenciador
        )