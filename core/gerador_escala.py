#Recebe o analista e monta a escala
# core/gerador_escala.py

import random
from collections import Counter


class GeradorEscala:

    def __init__(self, analistas, dias, horarios):

        self.analistas = analistas
        self.dias = dias
        self.horarios = horarios

        # Somente analistas disponíveis
        self.analistas_disponiveis = [
            analista
            for analista in analistas
            if analista is not None
            and isinstance(analista, dict)
            and analista.get("ativo", True)
            and not analista.get("ferias", False)
        ]

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def gerar(self, tentativas=5000):

        if not self.analistas_disponiveis:
            return None

        # Verifica antes se existe quantidade suficiente
        # de analistas para tentar montar a escala.
        if not self.verificar_viabilidade():
            return None

        # Cria todas as posições da escala
        posicoes = self.criar_posicoes()

        # Tenta gerar várias combinações
        for _ in range(tentativas):

            escala = {}

            quantidade_semanal = Counter()

            dias_utilizados = {
                dia: set()
                for dia in self.dias
            }

            # Em cada tentativa a ordem dos horários
            # pode mudar.
            ordem = posicoes.copy()

            random.shuffle(ordem)

            sucesso = self.preencher_escala(
                ordem,
                0,
                escala,
                quantidade_semanal,
                dias_utilizados
            )

            if sucesso:

                return escala

        return None

    # ==========================================================
    # CRIAR POSIÇÕES
    # ==========================================================

    def criar_posicoes(self):

        posicoes = []

        for dia in self.dias:

            for inicio, fim in self.horarios:

                posicoes.append(
                    (dia, inicio, fim)
                )

        return posicoes

    # ==========================================================
    # BACKTRACKING
    # ==========================================================

    def preencher_escala(
        self,
        posicoes,
        indice,
        escala,
        quantidade_semanal,
        dias_utilizados
    ):

        # Todas as posições foram preenchidas
        if indice >= len(posicoes):

            return self.verificar_minimos(
                quantidade_semanal
            )

        # Posição atual
        dia, inicio, fim = posicoes[indice]

        # Descobre quem pode trabalhar neste horário
        candidatos = self.obter_candidatos(
            dia,
            inicio,
            fim,
            quantidade_semanal,
            dias_utilizados
        )

        # Prioriza quem ainda precisa atingir
        # o mínimo semanal.
        candidatos.sort(
            key=lambda analista: (
                quantidade_semanal[
                    analista["nome"]
                ] >= analista.get(
                    "min_semana",
                    2
                ),

                quantidade_semanal[
                    analista["nome"]
                ]
            )
        )

        # Mistura candidatos que possuem
        # a mesma prioridade.
        random.shuffle(candidatos)

        for analista in candidatos:

            nome = analista["nome"]

            # Coloca o analista na escala
            escala[
                (dia, inicio, fim)
            ] = nome

            quantidade_semanal[nome] += 1

            dias_utilizados[dia].add(nome)

            # Verifica se ainda é possível atingir
            # os mínimos restantes.
            if self.ainda_eh_possivel(
                posicoes,
                indice + 1,
                quantidade_semanal,
                dias_utilizados
            ):

                sucesso = self.preencher_escala(
                    posicoes,
                    indice + 1,
                    escala,
                    quantidade_semanal,
                    dias_utilizados
                )

                if sucesso:
                    return True

            # --------------------------------------------------
            # DESFAZ A TENTATIVA
            # --------------------------------------------------

            del escala[
                (dia, inicio, fim)
            ]

            quantidade_semanal[nome] -= 1

            dias_utilizados[dia].remove(nome)

        return False

    # ==========================================================
    # OBTER CANDIDATOS
    # ==========================================================

    def obter_candidatos(
        self,
        dia,
        inicio,
        fim,
        quantidade_semanal,
        dias_utilizados
    ):

        candidatos = []

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            # ----------------------------------------------
            # Não pode aparecer duas vezes no mesmo dia
            # ----------------------------------------------

            if nome in dias_utilizados[dia]:
                continue

            # ----------------------------------------------
            # Verifica se o horário está dentro do turno
            # ----------------------------------------------

            if not self.horario_compativel(
                analista,
                inicio,
                fim
            ):
                continue

            if not self.horario_disponivel(
                analista,
                inicio,
                fim
            ):
                continue

            # ----------------------------------------------
            # Verifica limite semanal
            # ----------------------------------------------

            maximo = analista.get(
                "max_semana",
                2
            )

            if quantidade_semanal[nome] >= maximo:
                continue

            candidatos.append(
                analista
            )

        return candidatos

    # ==========================================================
    # VERIFICAR DISPONIBILIDADE DE HORÁRIO
    def horario_disponivel(
        self,
        analista,
        inicio,
        fim
    ):

        bloqueio = analista.get(
            "indisponivel",
            []
        )

        horario = f"{inicio}-{fim}"

        return horario not in bloqueio

    # ==========================================================
    # VERIFICAR HORÁRIO
    # ==========================================================

    def horario_compativel(
        self,
        analista,
        inicio,
        fim
    ):

        entrada = self.converter_hora(
            analista["entrada"]
        )

        saida = self.converter_hora(
            analista["saida"]
        )

        inicio_atendimento = self.converter_hora(
            inicio
        )

        fim_atendimento = self.converter_hora(
            fim
        )

        return (
            inicio_atendimento >= entrada
            and
            fim_atendimento <= saida
        )

    # ==========================================================
    # VERIFICAR MÍNIMOS
    # ==========================================================

    def verificar_minimos(
        self,
        quantidade_semanal
    ):

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            minimo = analista.get(
                "min_semana",
                2
            )

            if quantidade_semanal[nome] < minimo:

                return False

        return True

    # ==========================================================
    # VERIFICAR SE AINDA É POSSÍVEL
    # ==========================================================

    def ainda_eh_possivel(
        self,
        posicoes,
        indice,
        quantidade_semanal,
        dias_utilizados
    ):

        restantes = posicoes[indice:]

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            minimo = analista.get(
                "min_semana",
                2
            )

            atual = quantidade_semanal[nome]

            falta = minimo - atual

            # Já atingiu o mínimo
            if falta <= 0:
                continue

            # Quantos horários futuros ele poderia ocupar?
            oportunidades = 0

            for dia, inicio, fim in restantes:

                # Não pode repetir no mesmo dia
                if nome in dias_utilizados[dia]:
                    continue

                # Precisa caber no turno
                if not self.horario_compativel(
                    analista,
                    inicio,
                    fim
                ):
                    continue

                if not self.horario_disponivel(
                    analista,
                    inicio,
                    fim
                ):
                    continue

                oportunidades += 1

            # Não existem posições suficientes
            # para atingir o mínimo.
            if oportunidades < falta:

                return False

        return True

    # ==========================================================
    # VERIFICAR VIABILIDADE INICIAL
    # ==========================================================

    def verificar_viabilidade(self):

        quantidade_posicoes = (
            len(self.dias)
            *
            len(self.horarios)
        )

        # Soma dos mínimos
        minimo_total = 0

        for analista in self.analistas_disponiveis:

            minimo_total += analista.get(
                "min_semana",
                2
            )

        # Não pode exigir mais atendimentos
        # do que existem posições.
        if minimo_total > quantidade_posicoes:

            return False

        # Cada analista precisa ter pelo menos
        # uma quantidade de oportunidades suficiente
        # para alcançar seu mínimo.
        for analista in self.analistas_disponiveis:

            minimo = analista.get(
                "min_semana",
                2
            )

            oportunidades = 0

            for dia in self.dias:

                horarios_dia = 0

                for inicio, fim in self.horarios:

                    if (
                        self.horario_compativel(
                            analista,
                            inicio,
                            fim
                        )
                        and
                        self.horario_disponivel(
                            analista,
                            inicio,
                            fim
                        )
                    ):
                        horarios_dia += 1

                # Como o analista só pode aparecer uma vez
                # por dia, no máximo 1 oportunidade conta
                # para aquele dia.
                if horarios_dia > 0:
                    oportunidades += 1

            if oportunidades < minimo:

                return False

        return True

    # ==========================================================
    # CONVERTER HH:MM PARA MINUTOS
    # ==========================================================

    @staticmethod
    def converter_hora(hora):

        horas, minutos = map(
            int,
            hora.split(":")
        )

        return horas * 60 + minutos


# ==============================================================
# FUNÇÃO SIMPLIFICADA PARA USAR NA TELA PRINCIPAL
# ==============================================================

def gerar_escala(
    analistas,
    dias,
    horarios
):

    gerador = GeradorEscala(
        analistas,
        dias,
        horarios
    )

    return gerador.gerar()