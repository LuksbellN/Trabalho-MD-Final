"""Distribuição de clientes adimplentes e inadimplentes (dataset UCI 350).

Instalação: pip install pandas matplotlib
Execução: python distribuicao_clientes_inadimplentes.py

O gráfico é horizontal: eixo X = quantidade de clientes,
eixo Y = classes da variável alvo (0 e 1).
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent
CSV_LOCAL = BASE / "UCI_Credit_Card.csv"
CSV_URL = (
    "https://raw.githubusercontent.com/baopuzi/"
    "Credit_Default/master/UCI_Credit_Card.csv"
)
SAIDA = BASE / "distribuicao_clientes_inadimplentes.png"

# Usa arquivo local, se existir; senão, lê uma cópia pública da base.
fonte = CSV_LOCAL if CSV_LOCAL.exists() else CSV_URL
df = pd.read_csv(fonte)

# A coluna Y é o atributo classe da base (0 = adimplente; 1 = inadimplente).
coluna_alvo = next(
    (c for c in ("default.payment.next.month", "default payment next month", "Y") if c in df.columns),
    None,
)
if coluna_alvo is None:
    raise ValueError("A coluna-alvo Y não foi encontrada no CSV.")

contagens = df[coluna_alvo].value_counts().reindex([0, 1], fill_value=0)
classes = ["0 — Adimplente", "1 — Inadimplente"]
valores = contagens.to_list()

fig, ax = plt.subplots(figsize=(11.5, 5.7), dpi=150)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
barras = ax.barh(classes, valores, color="#092B6C", height=0.56)
ax.invert_yaxis()  # Adimplente em cima, inadimplente embaixo.

ax.set_title("Distribuição de clientes inadimplentes", fontsize=20, weight="bold", pad=22)
ax.set_xlabel("Quantidade de clientes", fontsize=13, labelpad=13)
ax.set_ylabel("Valores do atributo Y", fontsize=13, labelpad=12)

formata_br = lambda n: f"{n:,.0f}".replace(",", ".")
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: formata_br(x)))
ax.set_xlim(0, max(valores) * 1.18)
ax.xaxis.grid(True, alpha=0.25, color="#64748b", linewidth=0.8)
ax.set_axisbelow(True)
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.tick_params(axis="y", length=0, labelsize=12)
ax.tick_params(axis="x", labelsize=11)

for barra, valor in zip(barras, valores):
    percentual = valor / len(df) * 100
    rotulo = f"{formata_br(valor)} ({percentual:.2f}%)".replace(
        f"{percentual:.2f}", f"{percentual:.2f}".replace(".", ",")
    )
    ax.text(valor + max(valores) * 0.018,
            barra.get_y() + barra.get_height() / 2,
            rotulo, va="center", ha="left", fontsize=12,
            weight="bold", color="#13233b")

fig.text(0.5, 0.015, f"Fonte: UCI — Default of Credit Card Clients | Total: {formata_br(len(df))} clientes",
         ha="center", fontsize=10, color="#555")
plt.tight_layout(rect=(0, 0.065, 1, 1))
fig.savefig(SAIDA, dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Gráfico salvo em: {SAIDA}")
for categoria, valor in zip(classes, valores):
    print(f"{categoria}: {formata_br(valor)} clientes")
