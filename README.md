# GlobalSolution 

## ARES-7: Sistema de Monitoramento Espacial
---
### Estruturas de Dados e Lógica Computacional

O **Ares-7** é um ecossistema de software desenvolvido em Python voltado para a telemetria, diagnóstico de falhas e previsão de autonomia de recursos para uma estação habitacional aeroespacial simulada. 
.
O sistema consolida dados ambientais, analisa matrizes de consumo energético, rastreia anomalias em sensores e toma decisões automáticas em tempo real para salvaguardar a vida da tripulação.
---

## 1.Identificação
* **Nome da Aluno:** Marcos Henrique
* **Turma:** 1CCOC 2026/1
---

## 2. O Problema Analisado

No Ciclo 14, a estação ARES-7 enfrenta picos de radiação, instabilidade térmica e esvaziamento das baterias. Para piorar, o sensor de comunicação quebrou e passou a enviar leituras corrompidas de $-999\%$.

O sistema foi desenvolvido para resolver essa crise em três etapas:
* Filtrar anomalias: Identificar e isolar falsos dados de sensores.
* Priorizar alertas: Separar problemas leves de falhas críticas à vida.
* Prever o colapso: Calcular exatamente quando a energia vai acabar para agir antes do apagão.
---

## 3. Arquitetura e Estruturas de Dados Utilizadas

Para garantir performance algorítmica e conformidade com as boas práticas de Ciência da Computação, foi estruturado os dados da seguinte forma:

* **Dicionários (`dict`):** Utilizados para armazenar o `ambiente` e os estados binários (`1` para ativo, `0` para falha) dos `modulos`. Permitem buscas e atualizações imediatas com complexidade de tempo constante $O(1)$.
* **Matriz (`list` de `lists`):** A estrutura `matriz_energia` organiza os dados bidimensionais indexados por `[Horário, Variável]`, consolidando informações históricas de Geração, Consumo e Reserva.
* **Fila (`collections.deque`):** Implementa o comportamento **FIFO (First-In, First-Out)** para a `fila_alertas`. Garante que os logs de advertência sejam processados rigorosamente na ordem em que aconteceram cronologicamente.
* **Pilha (`list` com ordenação reversa):** Implementa o comportamento **LIFO (Last-In, First-Out)** para a `pilha_criticos`. Imprescindível para a tripulação, pois coloca o evento crítico *mais recente* no topo visual do painel de controle.

---

## 4. Regras Lógicas Principais de Diagnóstico

O motor de inferência do sistema utiliza condicionais aninhadas (`if`, `elif`, `else`) acopladas a operadores lógicos (`AND`, `OR`, `NOT`).

### A Expressão Booleana Principal
A regra mais crítica do sistema monitora a iminência de um apagão total através da combinação de capacidade atual e balanço energético:

$$\text{energia\_critica} = (\text{reserva\_atual} < 25) \land (\text{consumo\_atual} > \text{geracao\_atual})$$

---

## 5. Técnica de Previsão Utilizada e Resultados

Para antecipar crises e não apenas reagir a elas, implementamos de forma nativa o algoritmo de **Regressão Linear Simples por Mínimos Quadrados** para modelar o comportamento da reserva das baterias.

A função mapeia o tempo decorrido ($x$) em relação ao percentual de carga restante ($y$):

$$y = ax + b$$
