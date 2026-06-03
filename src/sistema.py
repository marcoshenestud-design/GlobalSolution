# Sistema de Monitoramento Espacial - Global Solution

from collections import deque

# status binário - 1=ativo, 0=falha
modulos = {
    "suporte_vida": 1,
    "energia": 1,
    "comunicacao": 0,
    "habitat": 1,
    "laboratorio": 1,
    "armazenamento": 1,
}

# Matriz: [geração kWh, consumo kWh, reserva %]
horarios = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]

matriz_energia = [
    [45, 38, 72],
    [62, 55, 74],
    [78, 82, 70],
    [71, 88, 58],
    [30, 91, 38],
    [12, 94, 22]
]

# Extração dos dados
reservas = [linha[2] for linha in matriz_energia]
geracoes = [linha[0] for linha in matriz_energia]
consumos = [linha[1] for linha in matriz_energia]

# Ambiente
ambiente = {
    "temperatura_interna": 21.5,
    "radiacao_mSv": 3.8,
    "qualidade_comunicacao": 34,
    "pressao_interna": 101.2
}

# Log de eventos
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

# ==================================================
# FILA E PILHA
# ==================================================

fila_alertas = deque(
    e for e in log_eventos
    if e[1] in ("ALERTA", "CRITICO", "FALHA")
)

pilha_criticos = [
    e for e in log_eventos
    if e[1] in ("CRITICO", "FALHA")
]

# ==================================================
# ANOMALIAS
# ==================================================

anomalias = []

for evento in log_eventos:
    hora, tipo, descricao = evento

    if "-999" in descricao:
        anomalias.append(evento)

# ==================================================
# REGRESSÃO LINEAR
# ==================================================

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

# ==================================================
# REGRAS DE DIAGNÓSTICO
# ==================================================

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

rad_critica = radiacao > 3.0
rad_alerta = 2.0 < radiacao <= 3.0

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

# Ordenação

alertas.sort(
    key=lambda x: 0 if x[0] == "CRITICO" else 1
)

# ==================================================
# STATUS GERAL
# ==================================================

if any(a[0] == "CRITICO" for a in alertas):
    status = "CRITICO"

elif any(a[0] == "ALERTA" for a in alertas):
    status = "ALERTA"

else:
    status = "NORMAL"

# ==================================================
# EXIBIÇÃO
# ==================================================

SEP = "=" * 58
LIN = "-" * 58

print("ARES-7 - MONITORAMENTO OPERACIONAL | Ciclo 14")
print(SEP)

print("\n[ MÓDULOS ]")

for nome, s in modulos.items():

    cond = "OK" if s else "FALHA"

    print(
        f"  {nome:<20} "
        f"[{cond:^5}] "
        f"{'Ativo' if s else 'INATIVO'}"
    )

print("\n[ ENERGIA — kWh / Reserva % ]")

print(
    f"  {'Hora':<6}"
    f"{'Gera':>8}"
    f"{'Cons':>8}"
    f"{'Res%':>8}"
    f"{'Saldo':>8}"
)

for i, h in enumerate(horarios):

    g, c, r = matriz_energia[i]

    saldo = g - c

    print(
        f"  {h:<6}"
        f"{g:>8}"
        f"{c:>8}"
        f"{r:>7}%"
        f"{saldo:>8}"
    )

print("\n[ AMBIENTE ]")

for chave, valor in ambiente.items():
    print(f"  {chave:<28} {valor}")

if anomalias:

    print("\n[ ANOMALIA DETECTADA ]")

    for a in anomalias:
        print(f"  {a[0]} - {a[2]}")

print("\n[ LOG DE EVENTOS ]")

for hora, tipo, desc in log_eventos:

    flag = " <<< ANOMALIA" if "-999" in desc else ""

    print(
        f"  {hora} "
        f"[{tipo:<7}] "
        f"{desc}{flag}"
    )

print("\n[ FILA DE ALERTAS PENDENTES - FIFO ]")

for i, (h, t, d) in enumerate(fila_alertas, 1):
    print(f"  {i}. {h} [{t}] {d}")

print("\n[ PILHA DE CRÍTICOS - topo = mais recente ]")

for i, (h, t, d) in enumerate(reversed(pilha_criticos)):

    marcador = "[TOPO]" if i == 0 else "      "

    print(f"  {marcador} {h} [{t}] {d}")

print("\n[ PREVISÃO - REGRESSÃO LINEAR DA RESERVA ]")

print(f"  Dados históricos: {reservas}")
print(f"  Modelo: y = {incl:.2f}x + {base:.2f}")

for i, p in enumerate(previsoes, 1):
    print(f"  Ciclo +{i}: {p}%")

print(f"\n[ DIAGNÓSTICO GERAL: *** {status} *** ]")

print(LIN)

for idx, (sev, mod, msg, acao) in enumerate(alertas, 1):

    icone = "[!!!]" if sev == "CRITICO" else "[ ! ]"

    print(f"  {idx}. {icone} {sev} - {mod}")
    print(f"     {msg}")
    print(f"     Ação: {acao}")

print(LIN)

total_criticos = sum(
    1 for a in alertas
    if a[0] == "CRITICO"
)

print(
    f"  Total: {len(alertas)} alertas "
    f"({total_criticos} críticos)"
)

print(SEP)