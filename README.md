# Databricks Pipeline Financial BCB

Automação em Python, orquestrada via BotCity, responsável pela extração diária de indicadores econômicos do Banco Central do Brasil (Selic, IPCA, CDI e Câmbio) e envio para o Data Lake no Databricks.

## Responsabilidade deste repositório

Este projeto cobre **apenas a etapa de extração** da pipeline: buscar o dado mais recente na fonte oficial e entregá-lo pronto para ingestão. O tratamento e as regras de negócio (camadas Bronze, Silver e Gold) rodam separadamente no Databricks, via PySpark.

```
API do Banco Central (SGS)
        │
        ▼
 ┌───────────────┐
 │    BotCity     │  ← este repositório
 │  extrai + envia │
 └───────────────┘
        │
        ▼
Databricks Volume (raw_files)
```

## O que o bot faz

1. Consulta a API do Banco Central (SGS) e busca a série mais recente de cada indicador
2. Aplica fallback automático em janelas de 10 anos para séries diárias, contornando a limitação de volume por requisição imposta pelo BCB desde mar/2025
3. Faz o upload do arquivo extraído diretamente para um Volume do Databricks (Unity Catalog), disponível para as próximas etapas do pipeline

Séries coletadas:

| Série | Código SGS | Frequência |
|---|---|---|
| Selic | 11 | Diária |
| IPCA | 433 | Mensal |
| CDI | 12 | Diária |
| Câmbio (USD) | 1 | Diária |

## Execução e agendamento

O bot roda diariamente, sem intervenção manual, agendado via **GitHub Actions** (workflow com `cron`) — garantindo que o dado mais recente de cada indicador esteja sempre disponível no Data Lake para as camadas seguintes de transformação.

## CI/CD (`.github/workflows/`)

Além do agendamento da extração diária, o repositório usa GitHub Actions para validar o código a cada push, mantendo a automação versionada, testável e sem depender de execução manual local.

## Stack

- **Python** — lógica de extração
- **BotCity / BotMaestro** — orquestração e agendamento diário
- **Databricks (Unity Catalog / Volumes)** — destino dos arquivos extraídos

## Status

🚧 Em desenvolvimento — extração automatizada funcionando; próximos passos incluem consolidar a camada de observabilidade do pipeline (log de execuções, sucesso/falha por série).
