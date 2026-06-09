from collections import deque

#estrutura de dados

modulos = {
    "suporte_vida": 1,
    "energia": 1,
    "comunicacao": 0,
    "habitat": 1,
    "laboratorio": 1,
    "armazenamento": 1,
}

#matriz
horarios = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
matriz_energia = [
    [45, 38, 72],
    [62, 55, 74],
    [78, 82, 70],
    [71, 88, 58],
    [30, 91, 38],
    [12, 94, 22]
]

# extração dos dados
reservas = [linha[2] for linha in matriz_energia]
geracoes = [linha[0] for linha in matriz_energia]
consumos = [linha[1] for linha in matriz_energia]

# ambiente
ambiente = {
    "temperatura_interna": 21.5,
    "radiacao_mSv": 3.8,
    "qualidade_comunicacao": 34,
    "pressao_interna": 101.2
}
# log de eventos
log_eventos = [
    ("04:12", "INFO", "Sistema inicializado — ciclo 14"),
    ("06:30", "ALERTA", "Qualidade de comunicação caiu para 60%"),
    ("09:45", "CRITICO", "Radiação ultrapassou 2.0 mSv/h"),
    ("11:20", "INFO", "Laboratório reiniciado após atualização"),
    ("14:00", "ALERTA", "Consumo superou geração solar"),
    ("16:30", "CRITICO", "Reserva de energia abaixo de 40%"),
    ("18:10", "FALHA", "Sensor de comunicação: leitura inválida -999%"),
    ("20:00", "INFO", "Modo de economia de energia ativado"),
]

# fila
fila_alertas = deque(
    e for e in log_eventos
    if e[1] in ("ALERTA", "CRITICO", "FALHA")
)

# pilha
pilha_criticos = [
    e for e in log_eventos
    if e[1] in ("CRITICO", "FALHA")
]
# ANOMALIAS

anomalias = []

for evento in log_eventos:
    hora, tipo, descricao = evento

    if "-999" in descricao:
        anomalias.append(evento)
# REGRESSÃO LINEAR

def regressao_linear(ys):
    n = len(ys)

    if n < 2:
        return 0, ys[0]

    xs = list(range(n))

    sx = sum(xs)
    sy = sum(ys)

    sxy = sum(xs[i] * ys[i] for i in range(n))
    sx2 = sum(x ** 2 for x in xs)

    a = (n * sxy - sx * sy) / (n * sx2 - sx ** 2)
    b = (sy - a * sx) / n

    return a, b


incl, base = regressao_linear(reservas)

previsoes = [
    round(max(0, incl * i + base), 1)
    for i in range(6, 9)
]
# REGRAS DE DIAGNÓSTICO

reserva_atual = reservas[-1]
consumo_atual = consumos[-1]
geracao_atual = geracoes[-1]

radiacao = ambiente["radiacao_mSv"]
qualidade_com = ambiente["qualidade_comunicacao"]

# Energia

energia_critica = (
    reserva_atual < 25
    and consumo_atual > geracao_atual
)

energia_baixa = (
    reserva_atual < 50
    and not energia_critica
)
# Comunicação

com_falha = (
    modulos["comunicacao"] == 0
    or qualidade_com < 40
)

com_fraca = (
    40 <= qualidade_com < 60
    and not com_falha
)
# Radiação

rad_critica = radiacao > 4.0
rad_alerta = 2.0 < radiacao <= 4.0
# Previsão

prev_critica = any(p < 15 for p in previsoes)

alertas = []
# Energia
if energia_critica or prev_critica:
    alertas.append(
        (
            "CRITICO",
            "energia",
            f"Reserva {reserva_atual}% — consumo ({consumo_atual} kWh) maior que geração ({geracao_atual} kWh).",
            "Desligar laboratório e sistemas não essenciais imediatamente."
        )
    )

elif energia_baixa:
    alertas.append(
        (
            "ALERTA",
            "energia",
            f"Reserva em {reserva_atual}%. Consumo elevado.",
            "Reduzir uso de sistemas secundários."
        )
    )
# Comunicação
if com_falha:
    alertas.append(
        (
            "CRITICO",
            "comunicacao",
            f"Módulo inativo. Qualidade: {qualidade_com}%.",
            "Ativar antena de backup e protocolo de emergência."
        )
    )
elif com_fraca:
    alertas.append(
        (
            "ALERTA",
            "comunicacao",
            f"Qualidade de sinal baixa: {qualidade_com}%.",
            "Reposicionar antena principal."
        )
    )
# Radiação
if rad_critica:
    alertas.append(
        (
            "CRITICO",
            "radiacao",
            f"Radiação: {radiacao} mSv/h.",
            "Evacuar áreas externas. Ativar blindagem do habitat."
        )
    )
elif rad_alerta:
    alertas.append(
        (
            "ALERTA",
            "radiacao",
            f"Radiação elevada: {radiacao} mSv/h.",
            "Monitorar e preparar evacuação."
        )
    )
# Suporte à vida
if not modulos["suporte_vida"]:
    alertas.append(
        (
            "CRITICO",
            "suporte_vida",
            "Módulo de suporte à vida INATIVO!",
            "EMERGÊNCIA MÁXIMA — ativar sistemas redundantes."
        )
    )
# Energia
if not modulos["energia"]:
    alertas.append(
        (
            "CRITICO",
            "energia",
            "Módulo de energia INATIVO!",
            "Ativar sistema de energia de emergência."
        )
    )
# Ordenação
alertas.sort(
    key=lambda x: 0 if x[0] == "CRITICO" else 1
)
# STATUS GERAL

if any(a[0] == "CRITICO" for a in alertas):
    status = "CRITICO"

elif any(a[0] == "ALERTA" for a in alertas):
    status = "ALERTA"

else:
    status = "NORMAL"
# EXIBIÇÃO
SEP = "=" * 58
LIN = "-" * 58

# MÓDULOS

print("\n[MÓDULOS]")
print(LIN)

nomes_modulos = {
    "suporte_vida": "Suporte à Vida",
    "energia": "Energia",
    "comunicacao": "Comunicação",
    "habitat": "Habitat",
    "laboratorio": "Laboratório",
    "armazenamento": "Armazenamento"
}

for chave, valor in modulos.items():

    status_mod = "OK" if valor else "FALHA"
    estado = "Ativo" if valor else "Inativo"

    print(
        f"{nomes_modulos[chave]:<18}: "
        f"{status_mod:<7} | {estado}"
    )

# ENERGIA
print("\n[ENERGIA - kWh / RESERVA]")
print(LIN)

print(
    f"{'Hora':<8}"
    f"{'Geração':>10}"
    f"{'Consumo':>10}"
    f"{'Reserva':>10}"
    f"{'Saldo':>9}"
)

print(LIN)

for i, hora in enumerate(horarios):

    g, c, r = matriz_energia[i]
    saldo = g - c

    print(
        f"{hora:<8}"
        f"{g:>10}"
        f"{c:>10}"
        f"{str(r)+'%':>10}"
        f"{saldo:>+9}"
    )

# AMBIENTE

print("\n[AMBIENTE]")
print(LIN)

print(f"Temperatura Interna    : {ambiente['temperatura_interna']} °C")
print(f"Radiação               : {ambiente['radiacao_mSv']} mSv/h")
print(f"Qualidade Comunicação  : {ambiente['qualidade_comunicacao']}%")
print(f"Pressão Interna        : {ambiente['pressao_interna']} kPa")

# ANOMALIA

if anomalias:

    print("\n[ANOMALIA DETECTADA]")
    print(LIN)

    for hora, tipo, descricao in anomalias:
        print(f"{hora} - {descricao}")

# LOG

print("\n[LOG DE EVENTOS]")
print(LIN)

for hora, tipo, descricao in log_eventos:

    print(
        f"{hora} "
        f"[{tipo:<8}] "
        f"{descricao}"
    )

# FILA

print("\n[FILA DE ALERTAS PENDENTES - FIFO]")
print(LIN)

for i, (hora, tipo, descricao) in enumerate(fila_alertas, 1):

    print(
        f"{i}. {hora} "
        f"[{tipo:<7}] "
        f"{descricao}"
    )

# PILHA

print("\n[PILHA DE CRÍTICOS - TOPO = MAIS RECENTE]")
print(LIN)

print("[TOPO]")

for hora, tipo, descricao in reversed(pilha_criticos):

    print(
        f"{hora} "
        f"[{tipo:<8}] "
        f"{descricao}"
    )

# PREVISÃO

print("\n[PREVISÃO - REGRESSÃO LINEAR DA RESERVA]")
print(LIN)

print("Dados históricos:")
print(reservas)

print("\nModelo:")
print(f"y = {incl:.2f}x + {base:.2f}")

print("\nPrevisão:")

for i, valor in enumerate(previsoes, 1):
    print(f"Ciclo +{i} : {valor}%")

# DIAGNÓSTICO

print("\n[DIAGNÓSTICO GERAL]")
print(LIN)

for i, (sev, mod, msg, acao) in enumerate(alertas, 1):

    print(f"{i}. {sev} - {mod.upper()}")

    print(f"   Problema: {msg}")
    print(f"   Ação    : {acao}")

    print()

# RESUMO

total_criticos = sum(
    1 for alerta in alertas
    if alerta[0] == "CRITICO"
)

print(LIN)
print("RESUMO")
print(LIN)

print(f"Alertas Totais    : {len(alertas)}")
print(f"Alertas Críticos  : {total_criticos}")
print(f"Reserva de Energia: {reserva_atual}%")

if com_falha:
    estado_com = "Inativa"
elif com_fraca:
    estado_com = "Fraca"
else:
    estado_com = "Ativa"

print(f"Comunicação       : {estado_com}")

print(f"Radiação          : {radiacao} mSv/h")
print(f"Estado Geral      : {status}")