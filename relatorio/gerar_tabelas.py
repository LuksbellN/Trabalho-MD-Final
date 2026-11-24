import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
METRICAS = ("f1_classe_1", "roc_auc", "acuracia_balanceada", "acuracia")
ROTULOS = {"n_neighbors": "k", "max_depth": "prof.", "C": "C"}


def quatro_casas(valor):
    return str(Decimal(valor).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)).replace(".", ",")


def parametro(configuracao):
    nome, valor = configuracao.split("=", 1)
    return f"{ROTULOS[nome]} = {valor.replace('.', ',')}"


def gerar_linhas(tabela, validacao=False):
    with (RAIZ / "results" / tabela).open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            config = parametro(linha["parametros"])
            if validacao:
                if linha["selecionado"] == "True":
                    config += r"\textsuperscript{*}"
                valores = [
                    quatro_casas(linha[f"{metrica}_media"])
                    + r"\,\(\pm\)\,"
                    + quatro_casas(linha[f"{metrica}_dp"])
                    for metrica in METRICAS
                ]
            else:
                valores = [quatro_casas(linha[metrica]) for metrica in METRICAS]
            yield " & ".join([linha["modelo"], config, *valores]) + r" \\" + "\n"


def main():
    parser = argparse.ArgumentParser(description="Gerar linhas LaTeX a partir dos resultados dos notebooks.")
    parser.add_argument("saida", type=Path)
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    for nome, validacao in (("validacao_cruzada", True), ("comparacao_teste", False)):
        linhas = gerar_linhas(f"{nome}.csv", validacao)
        (args.saida / f"tabela_{nome}.tex").write_text("".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    main()
