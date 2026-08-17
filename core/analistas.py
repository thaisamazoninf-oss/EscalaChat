# core/analistas.py

import json
import os


class GerenciadorAnalistas:

    def __init__(self):

        pasta_core = os.path.dirname(
            os.path.abspath(__file__)
        )

        pasta_projeto = os.path.dirname(
            pasta_core
        )

        pasta_dados = os.path.join(
            pasta_projeto,
            "dados"
        )

        self.arquivo = os.path.join(
            pasta_dados,
            "analistas.json"
        )

        self.criar_arquivo()

    # ======================================================
    # GARANTIR QUE O ARQUIVO EXISTA
    # ======================================================

    def criar_arquivo(self):

        # Cria a pasta dados caso não exista
        pasta = os.path.dirname(self.arquivo)

        if not os.path.exists(pasta):

            os.makedirs(pasta)

        # Cria o JSON caso não exista
        if not os.path.exists(self.arquivo):

            with open(
                self.arquivo,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    [],
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

    # ======================================================
    # CARREGAR
    # ======================================================

    def carregar(self):

        try:

            with open(
                self.arquivo,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(arquivo)

            # Garante que seja uma lista
            if not isinstance(dados, list):
                return []

            #Remove registros inválidos
            dados_validos = []

            for analista in dados:

                if not isinstance(analista, dict): 
                    continue

                if not analista.get("nome"):
                    continue

                dados_validos.append(analista)

            return dados_validos

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            return []

    # ======================================================
    # SALVAR
    # ======================================================

    def salvar(self, analistas):

        with open(
            self.arquivo,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                analistas,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    # ======================================================
    # ADICIONAR
    # ======================================================

    def adicionar(self, analista):

        analistas = self.carregar()

        # Verifica se já existe
        for existente in analistas:

            if existente["nome"].lower() == analista["nome"].lower():

                raise ValueError(
                    "Já existe um analista com esse nome."
                )

        analistas.append(
            analista
        )

        self.salvar(
            analistas
        )

    # ======================================================
    # EDITAR
    # ======================================================

    def editar(
        self,
        nome_antigo,
        novo_analista
    ):

        analistas = self.carregar()

        encontrado = False

        for indice, analista in enumerate(
            analistas
        ):

            if analista["nome"] == nome_antigo:

                analistas[indice] = novo_analista

                encontrado = True

                break

        if not encontrado:

            raise ValueError(
                f"Analista '{nome_antigo}' não encontrado."
            )

        self.salvar(
            analistas
        )

    # ======================================================
    # DESATIVAR
    # ======================================================

    def desativar(self, nome):

        analistas = self.carregar()

        for analista in analistas:

            if analista["nome"] == nome:

                analista["ativo"] = False

                self.salvar(
                    analistas
                )

                return

        raise ValueError(
            f"Analista '{nome}' não encontrado."
        )

    # ======================================================
    # ATIVAR
    # ======================================================

    def ativar(self, nome):

        analistas = self.carregar()

        for analista in analistas:

            if analista["nome"] == nome:

                analista["ativo"] = True

                # Se estava de férias, continuar
                # em férias.
                self.salvar(
                    analistas
                )

                return

        raise ValueError(
            f"Analista '{nome}' não encontrado."
        )

    # ======================================================
    # COLOCAR EM FÉRIAS
    # ======================================================

    def colocar_em_ferias(self, nome):

        analistas = self.carregar()

        for analista in analistas:

            if analista["nome"] == nome:

                analista["ferias"] = True

                self.salvar(
                    analistas
                )

                return

        raise ValueError(
            f"Analista '{nome}' não encontrado."
        )

    # ======================================================
    # RETIRAR DE FÉRIAS
    # ======================================================

    def retirar_de_ferias(self, nome):

        analistas = self.carregar()

        for analista in analistas:

            if analista["nome"] == nome:

                analista["ferias"] = False

                self.salvar(
                    analistas
                )

                return

        raise ValueError(
            f"Analista '{nome}' não encontrado."
        )

    # ======================================================
    # OBTER ANALISTAS ATIVOS
    # ======================================================

    def obter_ativos(self):

        analistas = self.carregar()

        return [
            analista
            for analista in analistas
            if analista.get("ativo", True)
            and not analista.get("ferias", False)
        ]

    # ======================================================
    # OBTER TODOS
    # ======================================================

    def obter_todos(self):

        return self.carregar()