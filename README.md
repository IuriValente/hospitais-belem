# Emergência Belém — encontre rápido o hospital de referência certo

Página web **offline-first** que ajuda uma pessoa em situação de urgência em **Belém-PA** a encontrar, em segundos, o pronto-socorro/hospital de **referência mais próximo capaz de atender a emergência específica** — por especialidade e por horário.

🔗 **Acesse:** https://iurivalente.github.io/hospitais-belem/

> ⚠️ **Aviso:** projeto **acadêmico, não-oficial**. **Não substitui atendimento médico nem o SAMU 192.** Em emergência com risco de vida, **ligue 192 antes de se deslocar**. As capacidades de alta complexidade são curadoria com incerteza — confirme sempre por telefone / 192.

Autor: **Iuri Valente Pires**

## O que faz

- **Triagem de 3 camadas** com fail-safe para o 192: risco de vida → tela "LIGUE 192 AGORA" + primeiros socorros; emergência estável → unidades de referência por proximidade; caso inespecífico → PS/UPA mais próximo ou 192.
- **Roteamento por especialidade**: infarto → hemodinâmica, AVC → TC + neuro, trauma → centro de trauma, obstétrica de alto risco, etc. — sempre com o **192 no topo** e um **PS geral 24h** próximo como retaguarda.
- **Primeiros socorros** (com o "o que **NÃO** fazer") revisados clinicamente.
- **Geolocalização no próprio aparelho** (ou seletor manual de bairro) + distância em linha reta.
- **Ações de 1 toque**: ligar 192, ligar o hospital, traçar rota, Disque-Intoxicação (envenenamento).

## Offline

É um **único arquivo HTML autossuficiente** (`index.html`) — baixe e abra no navegador; funciona **sem internet** (apenas o "traçar rota" usa o mapa online).

## Dados

- **CNES/DATASUS** (capacidade instalada georreferenciada) — 107 unidades de Belém + RMB.
- **Curadoria clínica** das capacidades de alta complexidade (hemodinâmica, AVC, trauma, obstétrica de referência), com nível de confiança e incerteza explícitos. Soro antiveneno e trombólise 24h permanecem incerteza ALTA até validação SESPA/SESMA/CIATOX-PA.

---
Uso "como está" (*as is*), sem garantias. Em emergência, **ligue 192**.
