from voz import ouvir, falar
from comandos import processar_comando

def main():
    while True:
        comando = ouvir()

        if not comando:
            continue

        if not processar_comando(comando, falar):
            break

if __name__ == "__main__":
    main()