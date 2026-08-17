# core/validacao.py

from collections import Counter


class ValidadorEscala:

    def __init__(self, analistas, dias, horarios):
        self.analistas = analistas
        self.dias = dias
        self.horarios = horarios

    # ==========================================================
    # VALIDAÇÃO PRINCIPAL
    # ==========================================================

    def validar(self, escala):

        erros = []

        erros.extend(
            self.validar_quantidade_atendimentos(escala)
        )

        erros.extend(
            self.validar_uma_vez_por_dia(escala)
        )

        erros.extend(
            self.validar_turnos(escala)
        )

        erros.extend(
            self.validar_minimo_semanal(escala)
        )

        erros.extend(
            self.validar_maximo_semanal(escala)
        )

        if erros:
            return False, erros

        return True, []

    # ==========================================================
    # 1. QUANTIDADE DE ATENDIMENTOS
    # ==========================================================

    def validar_quantidade_atendimentos(self, escala):

        erros = []

        quantidade_esperada = (
            len(self.dias) *
            len(self.horarios)
        )

        quantidade_real = len(escala)

        if quantidade_real != quantidade_esperada:

            erros.append(
                f"A escala possui {quantidade_real} "
                f"atendimentos, mas deveria possuir "
                f"{quantidade_esperada}."
            )

        return erros

    # ==========================================================
    # 2. UMA VEZ POR DIA
    # ==========================================================

    def validar_uma_vez_por_dia(self, escala):

        erros = []

        for dia in self.dias:

            nomes_do_dia = []

            for inicio, fim in self.horarios:

                nome = escala.get(
                    (dia, inicio, fim)
                )

                if nome:
                    nomes_do_dia.append(nome)

            contagem = Counter(
                nomes_do_dia
            )

            for nome, quantidade in contagem.items():

                if quantidade > 1:

                    erros.append(
                        f"{nome} aparece "
                        f"{quantidade} vezes na "
                        f"{dia}."
                    )

        return erros

    # ==========================================================
    # 3. VERIFICAR TURNO
    # ==========================================================

    def validar_turnos(self, escala):

        erros = []

        for (dia, inicio, fim), nome in escala.items():

            analista = self.buscar_analista(nome)

            if analista is None:

                erros.append(
                    f"{nome} não está cadastrado."
                )

                continue

            entrada = analista["entrada"]
            saida = analista["saida"]

            if (
                self.converter_hora(inicio)
                < self.converter_hora(entrada)
            ):

                erros.append(
                    f"{nome} foi escalado às "
                    f"{inicio} na {dia}, "
                    f"mas seu turno começa às "
                    f"{entrada}."
                )

            if (
                self.converter_hora(fim)
                > self.converter_hora(saida)
            ):

                erros.append(
                    f"{nome} foi escalado até "
                    f"{fim} na {dia}, "
                    f"mas seu turno termina às "
                    f"{saida}."
                )

        return erros

    # ==========================================================
    # 4. MÍNIMO SEMANAL
    # ==========================================================

    def validar_minimo_semanal(self, escala):

        erros = []

        contagem = self.contar_atendimentos(
            escala
        )

        for analista in self.analistas:

            nome = analista["nome"]

            minimo = analista.get(
                "min_semana",
                2
            )

            quantidade = contagem.get(
                nome,
                0
            )

            if quantidade < minimo:

                erros.append(
                    f"{nome} aparece apenas "
                    f"{quantidade} vez(es) na semana. "
                    f"O mínimo é {minimo}."
                )

        return erros

    # ==========================================================
    # 5. MÁXIMO SEMANAL
    # ==========================================================

    def validar_maximo_semanal(self, escala):

        erros = []

        contagem = self.contar_atendimentos(
            escala
        )

        for analista in self.analistas:

            nome = analista["nome"]

            maximo = analista.get(
                "max_semana",
                2
            )

            quantidade = contagem.get(
                nome,
                0
            )

            if quantidade > maximo:

                erros.append(
                    f"{nome} aparece "
                    f"{quantidade} vezes na semana. "
                    f"O máximo é {maximo}."
                )

        return erros

    # ==========================================================
    # CONTAR ATENDIMENTOS
    # ==========================================================

    def contar_atendimentos(self, escala):

        return Counter(
            escala.values()
        )

    # ==========================================================
    # BUSCAR ANALISTA
    # ==========================================================

    def buscar_analista(self, nome):

        for analista in self.analistas:

            if analista["nome"] == nome:

                return analista

        return None

    # ==========================================================
    # CONVERTER HORÁRIO
    # ==========================================================

    @staticmethod
    def converter_hora(hora):

        horas, minutos = map(
            int,
            hora.split(":")
        )

        return horas * 60 + minutos