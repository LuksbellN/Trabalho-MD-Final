from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
MEMBRO = "default of credit card clients.xls"
SHA256 = "30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933"
DESTINO = Path(__file__).with_name("default_credit_card_clients.xls")


def baixar():
    if DESTINO.exists() and sha256(DESTINO.read_bytes()).hexdigest() == SHA256:
        print(f"Base presente e íntegra: {DESTINO.name}")
        return

    with urlopen(URL, timeout=60) as resposta:
        with ZipFile(BytesIO(resposta.read())) as arquivo:
            dados = arquivo.read(MEMBRO)
    if sha256(dados).hexdigest() != SHA256:
        raise ValueError("O arquivo não corresponde à versão esperada da base UCI 350.")
    DESTINO.write_bytes(dados)
    print(f"Base UCI 350 baixada e verificada: {DESTINO.name}")


if __name__ == "__main__":
    baixar()
