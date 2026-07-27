from botcity.maestro import *
from databricks.sdk import WorkspaceClient
from datetime import datetime
import requests
import json
import os
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import io
from pathlib import Path

BotMaestroSDK.RAISE_NOT_CONNECTED = False
load_dotenv(Path(__file__).parent / ".env")

DESTINO_BASE = "/Volumes/finbancocentral/indicadores/raw_files"

SERIES_BCB = {
    "selic_diaria":   11,
    "ipca_mensal":   433,
    "cdi_diario":     12,
    "cambio_dolar":    1,
}

def buscar_serie (nome,codigo):

    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    response = requests.get(url, timeout=30)

    if response.status_code != 200:
     print(f">> Status code: {response.status_code}")
     data_list = []
     data_inicial = datetime(1984, 1, 1)
     data_final = datetime.today()

     while data_inicial < data_final:
         data_fim_janela = min(data_inicial + relativedelta(years=10), data_final)
         response = requests.get(
             f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={data_inicial.strftime('%d/%m/%Y')}&dataFinal={data_fim_janela.strftime('%d/%m/%Y')}")
         print(f">> Status janela: {response.status_code} | URL: {response.url}")
         data_list += response.json()
         data_inicial = data_fim_janela

     return json.dumps(data_list, ensure_ascii=False)

    return json.dumps(response.json(), ensure_ascii=False)

def exibir_previa(nome, dados_json, n=5):
    dados = json.loads(dados_json)
    print(f"\n>> Prévia '{nome}' ({n} primeiros registros):")
    for item in dados[:n]:
        print(f"   {item}")


def upload_databricks(nome, dados_json):

    w = WorkspaceClient(
        host=os.environ.get("DATABRICKS_HOST"),
        token=os.environ.get("DATABRICKS_TOKEN")
    )

    data_ingestao = datetime.now().strftime("%Y%m%d")
    destino = f"{DESTINO_BASE}/{nome}_{data_ingestao}.json"
    print(f"\n>> Uploading '{nome}' para: {destino}")
    w.files.upload(destino, io.BytesIO(dados_json.encode("utf-8")), overwrite=True)
    print(f">> Upload concluído!")

    return destino


def main():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    print(f">> Iniciando ingestão de {len(SERIES_BCB)} séries do BCB...\n")

    resultados = []

    for nome, codigo in SERIES_BCB.items():
        try:
            dados_json = buscar_serie(nome, codigo)
            exibir_previa(nome, dados_json)
            destino = upload_databricks(nome, dados_json)
            resultados.append({"serie": nome, "status": "ok", "destino": destino})
        except Exception as e:
            print(f">> ERRO na série '{nome}': {e}")
            resultados.append({"serie": nome, "status": "erro", "motivo": str(e)})

    print("\n>> ─── Resumo da execução ───")
    for r in resultados:
        status = "✅" if r["status"] == "ok" else "❌"
        print(f"   {status} {r['serie']}")

    print(f"\n>> Task ID: {execution.task_id}")
    print(f">> Parâmetros: {execution.parameters}")


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == "__main__":
    main()