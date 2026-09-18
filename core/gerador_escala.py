# ==============================================================
# Recebe os analistas e monta a escala
# core/gerador_escala.py
# ==============================================================

import random
import time
from collections import Counter

# ==============================================================
# GERADOR DE ESCALA
# core/gerador_escala.py
#
# Estratégia:
# - Backtracking inteligente
# - Escolhe primeiro as posições com menos candidatos
# - Respeita horários
# - Respeita indisponibilidade
# - Respeita mínimo e máximo semanal
# - Não repete analista no mesmo dia
# - Fase 1: tenta evitar dias consecutivos
# - Fase 2: permite dias consecutivos
# - Limite de tempo para evitar travamentos
# ==============================================================

import random
import time
from collections import Counter


class GeradorEscala:

    def __init__(self, analistas, dias, horarios):

        self.analistas = analistas
        self.dias = dias
        self.horarios = horarios

        # ------------------------------------------------------
        # ANALISTAS DISPONÍVEIS
        # ------------------------------------------------------

        self.analistas_disponiveis = [
            analista
            for analista in analistas
            if (
                analista is not None
                and isinstance(analista, dict)
                and analista.get("ativo", True)
                and not analista.get("ferias", False)
            )
        ]

        # ------------------------------------------------------
        # CONTROLE DE TEMPO
        # ------------------------------------------------------

        self.inicio_geracao = None
        self.limite_segundos = 5

        # ------------------------------------------------------
        # CONTROLE DE NÓS DO BACKTRACKING
        #
        # Evita uma quantidade absurda de combinações.
        # ------------------------------------------------------

        self.nos_visitados = 0
        self.limite_nos = 100000

        # ------------------------------------------------------
        # FASE 1:
        # False = não permite consecutivos
        #
        # FASE 2:
        # True = permite consecutivos
        # ------------------------------------------------------

        self.permitir_consecutivos = False

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def gerar(self, tentativas=500, limite_segundos=5):

        if not self.analistas_disponiveis:

            print("Nenhum analista disponível.")

            return None

        self.limite_segundos = limite_segundos
        self.inicio_geracao = time.time()

        # ------------------------------------------------------
        # VERIFICA VIABILIDADE
        # ------------------------------------------------------

        if not self.verificar_viabilidade():

            print()
            print(
                "Não foi possível gerar a escala: "
                "os critérios informados são inviáveis."
            )

            return None

        # ======================================================
        # FASE 1
        # ======================================================

        self.permitir_consecutivos = False
        self.nos_visitados = 0

        print()
        print("==========================================")
        print("FASE 1")
        print("Tentando gerar sem dias consecutivos...")
        print("==========================================")

        escala = self.tentar_gerar()

        if escala is not None:

            print()
            print("==========================================")
            print("ESCALA GERADA")
            print("Sem dias consecutivos.")
            print(
                f"Nós analisados: {self.nos_visitados}"
            )
            print("==========================================")

            return escala

        # ------------------------------------------------------
        # SE O TEMPO ACABOU, NÃO TENTA FASE 2
        # ------------------------------------------------------

        if self.tempo_esgotado():

            print()
            print(
                f"Geração interrompida após "
                f"{limite_segundos} segundos."
            )

            return None

        # ======================================================
        # FASE 2
        # ======================================================

        self.permitir_consecutivos = True
        self.nos_visitados = 0

        print()
        print("==========================================")
        print("FASE 2")
        print("Não foi possível gerar sem consecutivos.")
        print(
            "Tentando permitir dias consecutivos..."
        )
        print("==========================================")

        escala = self.tentar_gerar()

        if escala is not None:

            print()
            print("==========================================")
            print("ESCALA GERADA")
            print("Permitindo dias consecutivos.")
            print(
                f"Nós analisados: {self.nos_visitados}"
            )
            print("==========================================")

            return escala

        print()
        print("==========================================")
        print("FALHA")
        print(
            "Não foi possível gerar uma escala válida."
        )
        print(
            f"Nós analisados: {self.nos_visitados}"
        )
        print("==========================================")

        return None

    # ==========================================================
    # TENTAR GERAR
    # ==========================================================

    def tentar_gerar(self):

        # ------------------------------------------------------
        # POSIÇÕES
        # ------------------------------------------------------

        posicoes = self.criar_posicoes()

        if not posicoes:

            return None

        # ------------------------------------------------------
        # ESTRUTURAS
        # ------------------------------------------------------

        escala = {}

        quantidade_semanal = Counter()

        dias_utilizados = {
            dia: set()
            for dia in self.dias
        }

        dias_por_analista = {
            analista["nome"]: set()
            for analista in self.analistas_disponiveis
        }

        # ------------------------------------------------------
        # BACKTRACKING
        # ------------------------------------------------------

        sucesso = self.preencher_escala(
            posicoes,
            escala,
            quantidade_semanal,
            dias_utilizados,
            dias_por_analista
        )

        if sucesso:

            return escala

        return None

    # ==========================================================
    # CONTROLE DE TEMPO
    # ==========================================================

    def tempo_esgotado(self):

        if self.inicio_geracao is None:

            return False

        return (
            time.time() - self.inicio_geracao
            >= self.limite_segundos
        )

    # ==========================================================
    # CRIAR POSIÇÕES
    # ==============================================================

    def criar_posicoes(self):

        posicoes = []

        for dia in self.dias:

            for inicio, fim in self.horarios:

                posicoes.append(
                    (dia, inicio, fim)
                )

        return posicoes

    # ==========================================================
    # BACKTRACKING INTELIGENTE
    #
    # Escolhe sempre a posição com MENOS candidatos.
    #
    # Isso é muito mais eficiente do que embaralhar
    # todas as posições e tentar aleatoriamente.
    # ==========================================================

    def preencher_escala(
        self,
        posicoes,
        escala,
        quantidade_semanal,
        dias_utilizados,
        dias_por_analista
    ):

        # ------------------------------------------------------
        # CONTROLE DE TEMPO
        # ------------------------------------------------------

        if self.tempo_esgotado():

            return False

        # ------------------------------------------------------
        # CONTROLE DE NÓS
        # ------------------------------------------------------

        self.nos_visitados += 1

        if self.nos_visitados > self.limite_nos:

            return False

        # ------------------------------------------------------
        # TODAS AS POSIÇÕES PREENCHIDAS
        # ------------------------------------------------------

        if not posicoes:

            return self.verificar_minimos(
                quantidade_semanal
            )

        # ======================================================
        # ESCOLHER A POSIÇÃO MAIS DIFÍCIL
        # ======================================================

        melhor_posicao = None
        melhores_candidatos = None

        for posicao in posicoes:

            dia, inicio, fim = posicao

            candidatos = self.obter_candidatos(
                dia,
                inicio,
                fim,
                quantidade_semanal,
                dias_utilizados,
                dias_por_analista
            )

            # --------------------------------------------------
            # ZERO CANDIDATOS
            #
            # Não adianta continuar.
            # --------------------------------------------------

            if not candidatos:

                return False

            # --------------------------------------------------
            # MENOR DOMÍNIO
            # --------------------------------------------------

            if (
                melhores_candidatos is None
                or len(candidatos)
                < len(melhores_candidatos)
            ):

                melhor_posicao = posicao
                melhores_candidatos = candidatos

                # --------------------------------------------------
                # Se encontrou apenas 1 candidato, dificilmente
                # outra posição será mais restritiva.
                # --------------------------------------------------

                if len(candidatos) == 1:

                    break

        # ======================================================
        # POSIÇÃO ESCOLHIDA
        # ======================================================

        dia, inicio, fim = melhor_posicao

        candidatos = melhores_candidatos

        # ------------------------------------------------------
        # PRIORIZA QUEM AINDA PRECISA DO MÍNIMO
        # ------------------------------------------------------

        candidatos.sort(
            key=lambda analista: (
                -self.quantidade_necessaria(
                    analista,
                    quantidade_semanal
                ),

                quantidade_semanal[
                    analista["nome"]
                ]
            )
        )

        # ------------------------------------------------------
        # EMBARALHA EMPATES
        # ------------------------------------------------------

        random.shuffle(candidatos)

        # ------------------------------------------------------
        # TESTAR CANDIDATOS
        # ------------------------------------------------------

        for analista in candidatos:

            if self.tempo_esgotado():

                return False

            if self.nos_visitados > self.limite_nos:

                return False

            nome = analista["nome"]

            chave = (
                dia,
                inicio,
                fim
            )

            # --------------------------------------------------
            # COLOCA
            # --------------------------------------------------

            escala[chave] = nome

            quantidade_semanal[nome] += 1

            dias_utilizados[dia].add(nome)

            dias_por_analista[nome].add(dia)

            # --------------------------------------------------
            # REMOVE POSIÇÃO
            # --------------------------------------------------

            novas_posicoes = [
                pos
                for pos in posicoes
                if pos != melhor_posicao
            ]

            # --------------------------------------------------
            # VERIFICA POSSIBILIDADE
            # --------------------------------------------------

            possivel = self.ainda_eh_possivel(
                novas_posicoes,
                quantidade_semanal,
                dias_utilizados,
                dias_por_analista
            )

            if possivel:

                sucesso = self.preencher_escala(
                    novas_posicoes,
                    escala,
                    quantidade_semanal,
                    dias_utilizados,
                    dias_por_analista
                )

                if sucesso:

                    return True

            # --------------------------------------------------
            # DESFAZER
            # --------------------------------------------------

            del escala[chave]

            quantidade_semanal[nome] -= 1

            dias_utilizados[dia].remove(nome)

            dias_por_analista[nome].remove(dia)

        return False

    # ==========================================================
    # QUANTO O ANALISTA AINDA PRECISA
    # ==========================================================

    def quantidade_necessaria(
        self,
        analista,
        quantidade_semanal
    ):

        nome = analista["nome"]

        minimo = analista.get(
            "min_semana",
            2
        )

        atual = quantidade_semanal[nome]

        return max(
            0,
            minimo - atual
        )

    # ==========================================================
    # OBTER CANDIDATOS
    # ==========================================================

    def obter_candidatos(
        self,
        dia,
        inicio,
        fim,
        quantidade_semanal,
        dias_utilizados,
        dias_por_analista
    ):

        candidatos = []

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            # --------------------------------------------------
            # NÃO PODE REPETIR NO MESMO DIA
            # --------------------------------------------------

            if nome in dias_utilizados[dia]:

                continue

            # --------------------------------------------------
            # NÃO PODE TRABALHAR DIA CONSECUTIVO
            # NA FASE 1
            # --------------------------------------------------

            if not self.permitir_consecutivos:

                if self.trabalha_dia_anterior(
                    nome,
                    dia,
                    dias_por_analista
                ):

                    continue

            # --------------------------------------------------
            # HORÁRIO
            # --------------------------------------------------

            if not self.horario_compativel(
                analista,
                inicio,
                fim
            ):

                continue

            # --------------------------------------------------
            # INDISPONIBILIDADE
            # --------------------------------------------------

            if not self.horario_disponivel(
                analista,
                inicio,
                fim
            ):

                continue

            # --------------------------------------------------
            # MÁXIMO SEMANAL
            # --------------------------------------------------

            maximo = analista.get(
                "max_semana",
                2
            )

            if quantidade_semanal[nome] >= maximo:

                continue

            candidatos.append(analista)

        return candidatos

    # ==========================================================
    # VERIFICAR DIA ANTERIOR
    #
    # Importante:
    # Na construção da escala só precisamos verificar o dia
    # anterior que já foi atribuído.
    # ==========================================================

    def trabalha_dia_anterior(
        self,
        nome,
        dia,
        dias_por_analista
    ):

        indice = self.obter_indice_dia(
            dia
        )

        if indice is None:

            return False

        if indice == 0:

            return False

        dia_anterior = self.dias[
            indice - 1
        ]

        return (
            dia_anterior
            in dias_por_analista[nome]
        )

    # ==========================================================
    # VERIFICAR CONSECUTIVO
    # ==========================================================

    def trabalha_dia_consecutivo(
        self,
        nome,
        dia,
        dias_por_analista
    ):

        dias_trabalhados = dias_por_analista[
            nome
        ]

        indice_atual = self.obter_indice_dia(
            dia
        )

        if indice_atual is None:

            return False

        # ------------------------------------------------------
        # ANTERIOR
        # ------------------------------------------------------

        if indice_atual > 0:

            anterior = self.dias[
                indice_atual - 1
            ]

            if anterior in dias_trabalhados:

                return True

        # ------------------------------------------------------
        # POSTERIOR
        # ------------------------------------------------------

        if indice_atual < len(self.dias) - 1:

            posterior = self.dias[
                indice_atual + 1
            ]

            if posterior in dias_trabalhados:

                return True

        return False

    # ==========================================================
    # ÍNDICE DO DIA
    # ==========================================================

    def obter_indice_dia(self, dia):

        try:

            return self.dias.index(
                dia
            )

        except ValueError:

            return None

    # ==========================================================
    # HORÁRIO DISPONÍVEL
    # ==========================================================

    def horario_disponivel(
        self,
        analista,
        inicio,
        fim
    ):

        bloqueios = analista.get(
            "indisponivel",
            []
        )

        horario_atual = (
            f"{inicio}-{fim}"
            .replace(" ", "")
        )

        for bloqueio in bloqueios:

            bloqueio_normalizado = (
                str(bloqueio)
                .replace(" ", "")
            )

            if (
                horario_atual
                == bloqueio_normalizado
            ):

                return False

        return True

    # ==========================================================
    # HORÁRIO COMPATÍVEL
    # ==========================================================

    def horario_compativel(
        self,
        analista,
        inicio,
        fim
    ):

        try:

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

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            return False

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

            if (
                quantidade_semanal[nome]
                < minimo
            ):

                return False

        return True

    # ==========================================================
    # VERIFICAR SE AINDA É POSSÍVEL
    # ==========================================================

    def ainda_eh_possivel(
        self,
        posicoes,
        quantidade_semanal,
        dias_utilizados,
        dias_por_analista
    ):

        if self.tempo_esgotado():

            return False

        # ======================================================
        # PARA CADA ANALISTA
        # ======================================================

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            minimo = analista.get(
                "min_semana",
                2
            )

            maximo = analista.get(
                "max_semana",
                2
            )

            atual = quantidade_semanal[nome]

            # --------------------------------------------------
            # PASSOU DO MÁXIMO
            # --------------------------------------------------

            if atual > maximo:

                return False

            falta = minimo - atual

            if falta <= 0:

                continue

            # --------------------------------------------------
            # DIAS QUE AINDA PODE TRABALHAR
            # --------------------------------------------------

            dias_possiveis = set()

            for dia, inicio, fim in posicoes:

                # ----------------------------------------------
                # JÁ TRABALHOU NESSE DIA
                # ----------------------------------------------

                if nome in dias_utilizados[dia]:

                    continue

                # ----------------------------------------------
                # CONSECUTIVO
                # ----------------------------------------------

                if not self.permitir_consecutivos:

                    if self.dia_seria_consecutivo(
                        dia,
                        dias_por_analista[nome]
                    ):

                        continue

                # ----------------------------------------------
                # HORÁRIO
                # ----------------------------------------------

                if not self.horario_compativel(
                    analista,
                    inicio,
                    fim
                ):

                    continue

                # ----------------------------------------------
                # INDISPONIBILIDADE
                # ----------------------------------------------

                if not self.horario_disponivel(
                    analista,
                    inicio,
                    fim
                ):

                    continue

                dias_possiveis.add(dia)

            # --------------------------------------------------
            # NÃO HÁ DIAS SUFICIENTES
            # --------------------------------------------------

            if len(dias_possiveis) < falta:

                return False

        # ======================================================
        # CAPACIDADE TOTAL DAS POSIÇÕES RESTANTES
        # ======================================================

        capacidade_restante = 0

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            maximo = analista.get(
                "max_semana",
                2
            )

            capacidade_restante += (
                maximo
                - quantidade_semanal[nome]
            )

        if capacidade_restante < len(posicoes):

            return False

        return True

    # ==========================================================
    # TESTAR SE O DIA SERIA CONSECUTIVO
    # ==========================================================

    def dia_seria_consecutivo(
        self,
        dia,
        dias_trabalhados
    ):

        indice = self.obter_indice_dia(
            dia
        )

        if indice is None:

            return False

        # ------------------------------------------------------
        # DIA ANTERIOR
        # ------------------------------------------------------

        if indice > 0:

            anterior = self.dias[
                indice - 1
            ]

            if anterior in dias_trabalhados:

                return True

        # ------------------------------------------------------
        # DIA POSTERIOR
        # ------------------------------------------------------

        if indice < len(self.dias) - 1:

            posterior = self.dias[
                indice + 1
            ]

            if posterior in dias_trabalhados:

                return True

        return False

    # ==========================================================
    # VERIFICAR VIABILIDADE INICIAL
    # ==========================================================

    def verificar_viabilidade(self):

        quantidade_posicoes = (
            len(self.dias)
            *
            len(self.horarios)
        )

        # ======================================================
        # SOMA DOS MÍNIMOS
        # ======================================================

        minimo_total = 0
        maximo_total = 0

        for analista in self.analistas_disponiveis:

            minimo_total += analista.get(
                "min_semana",
                2
            )

            maximo_total += analista.get(
                "max_semana",
                2
            )

        # ------------------------------------------------------
        # MÍNIMO MAIOR QUE POSIÇÕES
        # ------------------------------------------------------

        if minimo_total > quantidade_posicoes:

            print()
            print("==========================================")
            print("ESCALA INVIÁVEL")
            print(
                f"Posições disponíveis: "
                f"{quantidade_posicoes}"
            )
            print(
                f"Mínimo necessário: "
                f"{minimo_total}"
            )
            print(
                "A soma dos mínimos é maior que "
                "o número de posições."
            )
            print("==========================================")

            return False

        # ------------------------------------------------------
        # MÁXIMO MENOR QUE POSIÇÕES
        # ------------------------------------------------------

        if maximo_total < quantidade_posicoes:

            print()
            print("==========================================")
            print("ESCALA INVIÁVEL")
            print(
                f"Posições necessárias: "
                f"{quantidade_posicoes}"
            )
            print(
                f"Capacidade máxima: "
                f"{maximo_total}"
            )
            print(
                "A soma dos máximos não é suficiente "
                "para preencher todas as posições."
            )
            print("==========================================")

            return False

        # ======================================================
        # VERIFICA CADA ANALISTA
        # ======================================================

        for analista in self.analistas_disponiveis:

            nome = analista["nome"]

            minimo = analista.get(
                "min_semana",
                2
            )

            maximo = analista.get(
                "max_semana",
                2
            )

            # --------------------------------------------------
            # MÍNIMO > MÁXIMO
            # --------------------------------------------------

            if minimo > maximo:

                print()
                print("==========================================")
                print("ESCALA INVIÁVEL")
                print(
                    f"Analista: {nome}"
                )
                print(
                    f"Mínimo: {minimo}"
                )
                print(
                    f"Máximo: {maximo}"
                )
                print(
                    "O mínimo semanal é maior "
                    "que o máximo."
                )
                print("==========================================")

                return False

            # ==================================================
            # DIAS POSSÍVEIS
            # ==================================================

            dias_possiveis = []

            for dia in self.dias:

                possui_horario = False

                for inicio, fim in self.horarios:

                    # ------------------------------------------
                    # HORÁRIO
                    # ------------------------------------------

                    if not self.horario_compativel(
                        analista,
                        inicio,
                        fim
                    ):

                        continue

                    # ------------------------------------------
                    # INDISPONIBILIDADE
                    # ------------------------------------------

                    if not self.horario_disponivel(
                        analista,
                        inicio,
                        fim
                    ):

                        continue

                    possui_horario = True

                    break

                if possui_horario:

                    dias_possiveis.append(
                        dia
                    )

            # --------------------------------------------------
            # NÃO POSSUI DIAS SUFICIENTES
            # --------------------------------------------------

            if len(dias_possiveis) < minimo:

                print()
                print("==========================================")
                print("ESCALA INVIÁVEL")
                print(
                    f"Analista: {nome}"
                )
                print(
                    f"Mínimo necessário: "
                    f"{minimo}"
                )
                print(
                    f"Dias possíveis: "
                    f"{len(dias_possiveis)}"
                )
                print(
                    f"Dias disponíveis: "
                    f"{dias_possiveis}"
                )
                print(
                    "O analista não possui dias "
                    "suficientes para atingir "
                    "o mínimo."
                )
                print("==========================================")

                return False

            # ==================================================
            # DIAS ALTERNADOS
            # ==================================================

            max_dias_alternados = (
                self.calcular_max_dias_alternados(
                    dias_possiveis
                )
            )

            if max_dias_alternados < minimo:

                print(
                    f"Atenção: {nome} precisa de "
                    f"{minimo} dias, mas possui "
                    f"apenas {max_dias_alternados} "
                    f"dias possíveis sem consecutivos."
                )

                print(
                    "A Fase 2 poderá permitir "
                    "dias consecutivos."
                )

        return True

    # ==========================================================
    # CALCULAR MÁXIMO DE DIAS ALTERNADOS
    #
    # Exemplo:
    #
    # Dias possíveis:
    #
    # 1, 2, 3, 4, 5
    #
    # Máximo sem consecutivos:
    #
    # 1, 3, 5 = 3
    #
    # ==========================================================

    def calcular_max_dias_alternados(
        self,
        dias_possiveis
    ):

        if not dias_possiveis:

            return 0

        indices = sorted(
            self.obter_indice_dia(dia)
            for dia in dias_possiveis
            if self.obter_indice_dia(dia) is not None
        )

        if not indices:

            return 0

        # ------------------------------------------------------
        # PROGRAMAÇÃO DINÂMICA
        #
        # dp[i] = maior quantidade de dias alternados
        # até o índice i.
        # ------------------------------------------------------

        dp = [1] * len(indices)

        for i in range(len(indices)):

            for j in range(i):

                if indices[i] > indices[j] + 1:

                    dp[i] = max(
                        dp[i],
                        dp[j] + 1
                    )

        maximo = max(dp)

        # ------------------------------------------------------
        # LIMITE TEÓRICO
        # ------------------------------------------------------

        limite_teorico = (
            len(self.dias) + 1
        ) // 2

        return min(
            maximo,
            limite_teorico
        )

    # ==========================================================
    # CONVERTER HH:MM PARA MINUTOS
    # ==========================================================

    @staticmethod
    def converter_hora(hora):

        horas, minutos = map(
            int,
            str(hora).split(":")
        )

        return horas * 60 + minutos


# ==============================================================
# FUNÇÃO SIMPLIFICADA PARA A TELA PRINCIPAL
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

    return gerador.gerar(
        limite_segundos=5
    )



