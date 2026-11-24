"""Gera dois gráficos com dados reais do UCI Default of Credit Card Clients.

Instalação: pip install pandas matplotlib numpy
Execução: python graficos_credito.py
Entrada: UCI_Credit_Card.csv no mesmo diretório, se disponível; senão tenta baixar
         a cópia pública do dataset no GitHub.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

DIR = Path(__file__).resolve().parent
DATA_FILE = DIR / "UCI_Credit_Card.csv"
DATA_URL = "https://raw.githubusercontent.com/baopuzi/Credit_Default/master/UCI_Credit_Card.csv"
AZUL = "#082b69"


def pt_int(x, pos=None):
    return f"{int(x):,}".replace(",", ".")


def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        origem = str(DATA_FILE)
    else:
        df = pd.read_csv(DATA_URL)
        origem = DATA_URL
    expected = ["LIMIT_BAL", "AGE"] + [f"BILL_AMT{i}" for i in range(1, 7)] + [f"PAY_AMT{i}" for i in range(1, 7)]
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    if len(df) != 30000:
        raise ValueError(f"Esperados 30.000 clientes; encontrados {len(df)}. Origem: {origem}")
    return df, expected


def configure_axis(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#c4cad2", linewidth=0.75, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(pt_int))


def chart_outliers(df, cols):
    counts = []
    records = []
    for name in cols:
        series = pd.to_numeric(df[name], errors="raise").dropna()
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        quantity = int(((series < lower) | (series > upper)).sum())
        counts.append(quantity)
        records.append({"Atributo": name, "Q1": q1, "Q3": q3, "IQR": iqr,
                        "Limite inferior": lower, "Limite superior": upper,
                        "Quantidade de outliers": quantity,
                        "Percentual (%)": round(quantity / len(series) * 100, 2)})

    fig, ax = plt.subplots(figsize=(18, 8.4), dpi=160)
    bars = ax.bar(cols, counts, color=AZUL, width=0.78)
    configure_axis(ax)
    ax.bar_label(bars, labels=[pt_int(n) for n in counts], padding=5,
                 fontsize=10, fontweight="bold", color="#111827")
    ax.set_title("Outliers detectados pela regra 1,5 × IQR", fontsize=22,
                 fontweight="bold", pad=18)
    ax.text(0.5, 1.005, "Dataset: Default of Credit Card Clients",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=12, style="italic")
    ax.set_xlabel("Atributos", fontsize=13, labelpad=10)
    ax.set_ylabel("Quantidade de outliers", fontsize=13)
    ax.tick_params(axis="x", labelrotation=45, labelsize=10)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    ax.set_ylim(0, max(counts) * 1.14)
    fig.text(0.5, 0.015, "Regra: valores < Q1 − 1,5 × IQR ou > Q3 + 1,5 × IQR | 30.000 clientes",
             ha="center", fontsize=10, color="#475569")
    fig.subplots_adjust(top=0.84, bottom=0.21, left=0.08, right=0.98)
    path = DIR / "outliers_iqr.png"
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    return pd.DataFrame(records), path


def chart_limit(df):
    values = pd.to_numeric(df["LIMIT_BAL"], errors="raise")
    # Intervalos iguais de NT$ 100.000; incluir explicitamente o máximo observado.
    bin_width = 100000
    upper = int(np.ceil(values.max() / bin_width) * bin_width + bin_width)
    bins = np.arange(0, upper + 1, bin_width)
    hist, edges = np.histogram(values, bins=bins)

    fig, ax = plt.subplots(figsize=(15, 8), dpi=160)
    bars = ax.bar(edges[:-1], hist, width=np.diff(edges), align="edge",
                  color=AZUL, edgecolor="white", linewidth=1.3)
    configure_axis(ax)
    ax.bar_label(bars, labels=[pt_int(n) if n else "" for n in hist],
                 padding=5, fontsize=10, fontweight="bold", color="#111827")
    ax.set_title("Distribuição do limite de crédito entre os clientes",
                 fontsize=20, fontweight="bold", pad=18)
    ax.text(0.5, 1.005, "X1 — LIMIT_BAL | Default of Credit Card Clients",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=12)
    ax.set_xlabel("Limite de crédito (NT$)", fontsize=13, labelpad=12)
    ax.set_ylabel("Quantidade de clientes", fontsize=13)
    ax.set_xlim(0, edges[-1])
    ax.set_ylim(0, max(hist) * 1.17)
    ax.xaxis.set_major_locator(MultipleLocator(100000))
    ax.xaxis.set_major_formatter(FuncFormatter(pt_int))
    ax.tick_params(axis="x", labelrotation=35, labelsize=10)
    fig.text(0.5, 0.015, "Base completa: 30.000 clientes | Intervalos de NT$ 100.000",
             ha="center", fontsize=10, color="#475569")
    fig.subplots_adjust(top=0.84, bottom=0.2, left=0.095, right=0.98)
    path = DIR / "distribuicao_limite_credito.png"
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    return pd.DataFrame({"Faixa inicial (NT$)": edges[:-1],
                         "Faixa final (NT$)": edges[1:],
                         "Quantidade de clientes": hist}), path


def main():
    df, cols = load_data()
    iqr, image1 = chart_outliers(df, cols)
    dist, image2 = chart_limit(df)
    iqr.to_csv(DIR / "resumo_outliers_iqr.csv", index=False)
    dist.to_csv(DIR / "frequencias_limite_credito.csv", index=False)
    print("Arquivos gerados:", image1, image2, sep="\n")
    print("\nContagem real de outliers por atributo:\n", iqr[["Atributo", "Quantidade de outliers"]].to_string(index=False))
    print("\nFrequências dos limites de crédito:\n", dist.to_string(index=False))


if __name__ == "__main__":
    main()
