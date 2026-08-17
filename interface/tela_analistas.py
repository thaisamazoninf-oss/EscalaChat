import tkinter as tk
from tkinter import ttk, messagebox

from core.regras import HORARIOS


class TelaAnalistas:

    def __init__(self, janela, gerenciador):

        self.janela = janela
        self.gerenciador = gerenciador

        self.janela.title(
            "Gerenciamento de Analistas"
        )

        self.janela.geometry(
            "850x550"
        )

        self.criar_interface()

        self.carregar_analistas()

    # ======================================================
    # INTERFACE
    # ======================================================

    def criar_interface(self):

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        titulo = tk.Label(
            self.janela,
            text="GERENCIAR ANALISTAS",
            font=("Arial", 18, "bold")
        )

        titulo.pack(
            pady=(20, 15)
        )

        # --------------------------------------------------
        # TOTAL ANALISTAS
        # --------------------------------------------------
        self.label_quantidade = tk.Label(
            self.janela,
            text="Total de analistas: 0",
            font=("Arial", 12, "bold")
        )

        self.label_quantidade.pack(
            pady=(0, 10)
        )

        # --------------------------------------------------
        # TABELA
        # --------------------------------------------------

        frame_tabela = tk.Frame(
            self.janela
        )

        frame_tabela.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        colunas = (
            "numero",
            "nome",
            "turno",
            "minimo",
            "maximo",
            "status"
        )

        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        self.tabela.heading(
            "numero",
            text="Nº"
        )
        
        self.tabela.heading(
            "nome",
            text="Nome"
        )

        self.tabela.heading(
            "turno",
            text="Turno"
        )

        self.tabela.heading(
            "minimo",
            text="Mínimo"
        )

        self.tabela.heading(
            "maximo",
            text="Máximo"
        )

        self.tabela.heading(
            "status",
            text="Situação"
        )

        self.tabela.column(
            "numero",
            width=50,
            anchor="center"
        )

        self.tabela.column(
            "nome",
            width=250,
            anchor="w"
        )

        self.tabela.column(
            "turno",
            width=120,
            anchor="center"
        )

        self.tabela.column(
            "minimo",
            width=80,
            anchor="center"
        )

        self.tabela.column(
            "maximo",
            width=80,
            anchor="center"
        )

        self.tabela.column(
            "status",
            width=150,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            frame_tabela,
            orient="vertical",
            command=self.tabela.yview
        )

        self.tabela.configure(
            yscrollcommand=scrollbar.set
        )

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # --------------------------------------------------
        # BOTÕES
        # --------------------------------------------------

        frame_botoes = tk.Frame(
            self.janela
        )

        frame_botoes.pack(
            pady=15
        )

        tk.Button(
            frame_botoes,
            text="Novo",
            width=14,
            command=self.novo_analista
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="Editar",
            width=14,
            command=self.editar_analista
        ).pack(
            side="left",
            padx=5
        )

        self.botao_ferias = tk.Button(
            frame_botoes,
            text="Férias",
            width=14,
            command=self.alterar_ferias
        )

        self.botao_ferias.pack(
            side="left",    
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="Ativar",
            width=14,
            command=self.ativar_analista
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="Desativar",
            width=14,
            command=self.desativar_analista
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="Fechar",
            width=14,
            command=self.janela.destroy
        ).pack(
            side="left",
            padx=5
        )

    # ======================================================
    # CARREGAR ANALISTAS
    # ======================================================

    def carregar_analistas(self):

        # Limpa a tabela

        for item in self.tabela.get_children():

            self.tabela.delete(item)

        # Busca todos os analistas

        analistas = self.gerenciador.carregar()

        #Ordena os analistas por nome
        analistas = sorted(
            analistas,
            key=lambda analista: analista["nome"].lower()
        )

        # Quantidade total
        quantidade = len(analistas)

        self.label_quantidade.config(
            text=f"Total de analistas: {quantidade}"
        )

        # Insere os analistas
        for numero, analista in enumerate(
            analistas, 
            start=1
        ):

            nome = analista["nome"]

            entrada = analista["entrada"]
            saida = analista["saida"]

            turno = (
                f"{entrada}–{saida}"
            )

            minimo = analista.get(
                "min_semana",
                2
            )

            maximo = analista.get(
                "max_semana",
                2
            )

            # ------------------------------------------
            # SITUAÇÃO
            # ------------------------------------------

            if not analista.get(
                "ativo",
                True
            ):

                status = "Desativado"

            elif analista.get(
                "ferias",
                False
            ):

                status = "Férias"

            else:

                status = "Ativo"

            self.tabela.insert(
                "",
                "end",
                iid=nome,
                values=(
                    numero,
                    nome,
                    turno,
                    minimo,
                    maximo,
                    status
                )
            )

    # ======================================================
    # ANALISTA SELECIONADO
    # ======================================================

    def obter_selecionado(self):

        selecionado = self.tabela.selection()

        if not selecionado:

            messagebox.showwarning(
                "Atenção",
                "Selecione um analista."
            )

            return None

        nome = selecionado[0]

        analistas = self.gerenciador.carregar()

        for analista in analistas:

            if analista["nome"] == nome:

                return analista

        return None

    # ======================================================
    # NOVO ANALISTA
    # ======================================================

    def novo_analista(self):

        janela = tk.Toplevel(
            self.janela
        )

        janela.title(
            "Novo Analista"
        )

        janela.geometry(
            "400x400"
        )

        janela.transient(
            self.janela
        )

        self.formulario_analista(
            janela
        )

    # ======================================================
    # FORMULÁRIO
    # ======================================================

    def formulario_analista(
        self,
        janela,
        analista=None
    ):

        frame = tk.Frame(
            janela
        )

        frame.pack(
            padx=30,
            pady=25,
            fill="both",
            expand=True
        )

        # Nome

        tk.Label(
            frame,
            text="Nome:"
        ).pack(
            anchor="w"
        )

        entrada_nome = tk.Entry(
            frame
        )

        entrada_nome.pack(
            fill="x",
            pady=(0, 15)
        )

        # Entrada

        tk.Label(
            frame,
            text="Horário de entrada:"
        ).pack(
            anchor="w"
        )

        entrada_inicio = tk.Entry(
            frame
        )

        entrada_inicio.pack(
            fill="x",
            pady=(0, 15)
        )

        # Saída

        tk.Label(
            frame,
            text="Horário de saída:"
        ).pack(
            anchor="w"
        )

        entrada_saida = tk.Entry(
            frame
        )

        entrada_saida.pack(
            fill="x",
            pady=(0, 15)
        )

        # Mínimo

        tk.Label(
            frame,
            text="Mínimo por semana:"
        ).pack(
            anchor="w"
        )

        entrada_minimo = tk.Entry(
            frame
        )

        entrada_minimo.pack(
            fill="x",
            pady=(0, 15)
        )

        # Máximo

        tk.Label(
            frame,
            text="Máximo por semana:"
        ).pack(
            anchor="w"
        )

        entrada_maximo = tk.Entry(
            frame
        )

        entrada_maximo.pack(
            fill="x",
            pady=(0, 15)
        )

        # --------------------------------------------------
        # HORÁRIOS INDISPONÍVEIS
        # --------------------------------------------------
        tk.Label(
            frame,
            text="Horários indisponíveis:"
        ).pack(
            anchor="w",
            pady=(5,5)
        )

        frame_horarios = tk.Frame(
            frame   
        )

        frame_horarios.pack(
            fill="x",
            pady=(0, 15)
        )

        variaveis_horarios = {}

        for inicio, fim in HORARIOS:

            horario = f"{inicio}–{fim}"

            variavel = tk.BooleanVar(
                value=False
            )

            variaveis_horarios[horario] = variavel

            tk.Checkbutton(
                frame_horarios,
                text=f"{inicio.replace(':', 'h')}-{fim.replace(':', 'h')}",
                variable=variavel,
                anchor="w"
            ).pack(
                anchor="w"
            )

            variaveis_horarios[horario] = variavel

        # --------------------------------------------------
        # EDITANDO
        # --------------------------------------------------

        if analista:

            entrada_nome.insert(
                0,
                analista["nome"]
            )

            entrada_inicio.insert(
                0,
                analista["entrada"]
            )

            entrada_saida.insert(
                0,
                analista["saida"]
            )

            entrada_minimo.insert(
                0,
                analista.get(
                    "min_semana",
                    2
                )
            )

            entrada_maximo.insert(
                0,
                analista.get(
                    "max_semana",
                    2
                )

            )

            #carregar horários indisponíveis
            horarios_indisponiveis = analista.get(
                "indisponivel",
                []
            )

            for horario, variavel in variaveis_horarios.items():

                if horario in horarios_indisponiveis:

                    variavel.set(True)

        # --------------------------------------------------
        # SALVAR
        # --------------------------------------------------

        def salvar():

            nome = entrada_nome.get().strip()
            entrada = entrada_inicio.get().strip()
            saida = entrada_saida.get().strip()

            try:

                minimo = int(
                    entrada_minimo.get()
                )

                maximo = int(
                    entrada_maximo.get()
                )

            except ValueError:

                messagebox.showerror(
                    "Erro",
                    "Mínimo e máximo devem ser números."
                )

                return

            if not nome:

                messagebox.showwarning(
                    "Atenção",
                    "Informe o nome do analista."
                )

                return

            if minimo < 0:

                messagebox.showwarning(
                    "Atenção",
                    "O mínimo não pode ser negativo."
                )

                return

            if maximo < minimo:

                messagebox.showwarning(
                    "Atenção",
                    "O máximo não pode ser menor "
                    "que o mínimo."
                )

                return


            horarios_indisponiveis = [
                horario
                for horario, variavel in variaveis_horarios.items()
                if variavel.get()
            ]

            novo = {
                "nome": nome,
                "entrada": entrada,
                "saida": saida,
                "min_semana": minimo,
                "max_semana": maximo,
                "ativo": True,
                "ferias": False,
                "indisponivel": horarios_indisponiveis
            }

            if analista:

                novo["ativo"] = analista.get(
                    "ativo",
                    True
                )

                novo["ferias"] = analista.get(
                    "ferias",
                    False
                )

                self.gerenciador.editar(
                    analista["nome"],
                    novo
                )

            else:

                self.gerenciador.adicionar(
                    novo
                )

            self.carregar_analistas()

            janela.destroy()

        tk.Button(
            frame,
            text="Salvar",
            width=15,
            command=salvar
        ).pack(
            pady=10
        )

    # ======================================================
    # EDITAR
    # ======================================================

    def editar_analista(self):

        analista = self.obter_selecionado()

        if not analista:
            return

        janela = tk.Toplevel(
            self.janela
        )

        janela.title(
            "Editar Analista"
        )

        janela.geometry(
            "400x400"
        )

        janela.transient(
            self.janela
        )

        self.formulario_analista(
            janela,
            analista
        )

    # ======================================================
    # FÉRIAS
    # ======================================================

    def alterar_ferias(self):
        analista = self.obter_selecionado()

        if not analista:
            return

        nome = analista["nome"]

        #Se já está de férias, retorna das férias.
        if analista.get(
            "ferias",
            False
        ):
            resposta = messagebox.askyesno(
                "Retornar de férias",
                f"Deseja retirar {nome} das férias?"
            )

            if not resposta:
                return

            self.gerenciador.retirar_de_ferias(
                nome
            )

        else:
            resposta = messagebox.askyesno(
                "Férias",
                f"Deseja colocar {nome} em férias?"
            )

            if not resposta:
                return

            self.gerenciador.colocar_em_ferias(
                nome
            )

        self.carregar_analistas()
    # ======================================================
    # ATIVAR
    # ======================================================

    def ativar_analista(self):

        analista = self.obter_selecionado()

        if not analista:
            return

        nome = analista["nome"]

        self.gerenciador.ativar(
            nome
        )

        self.carregar_analistas()

    # ======================================================
    # DESATIVAR
    # ======================================================

    def desativar_analista(self):

        analista = self.obter_selecionado()

        if not analista:
            return

        nome = analista["nome"]

        resposta = messagebox.askyesno(
            "Desativar analista",
            f"Deseja realmente desativar "
            f"{nome}?"
        )

        if not resposta:
            return

        self.gerenciador.desativar(
            nome
        )

        self.carregar_analistas()