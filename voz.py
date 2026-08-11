import subprocess
import tempfile
import winsound
from pathlib import Path
import speech_recognition as sr

BASE_DIR = Path(__file__).resolve().parent
MODELO_VOZ = BASE_DIR / "voices" / "pt_BR-cadu-medium.onnx"

reconhecedor = sr.Recognizer()

def falar(texto):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as arquivo:
        caminho_audio = Path(arquivo.name)

    try:
        subprocess.run(
            [
                "piper",
                "--model",
                str(MODELO_VOZ),
                "--output_file",
                str(caminho_audio)
            ],
            input=texto,
            text=True,
            check=True
        )

        winsound.PlaySound(
            str(caminho_audio),
            winsound.SND_FILENAME
        )

    finally:
        caminho_audio.unlink(missing_ok=True)

def ouvir():
    with sr.Microphone() as source:
        reconhecedor.adjust_for_ambient_noise(source, duration=1)
        print("Ouvindo...")

        try:
            audio = reconhecedor.listen(
                source,
                timeout=5,
                phrase_time_limit=6
            )

            comando = reconhecedor.recognize_google(
                audio,
                language="pt-BR"
            )

            print(f"Você disse: {comando}")
            return comando.lower().strip()

        except sr.WaitTimeoutError:
            print("Nenhuma fala detectada.")

        except sr.UnknownValueError:
            print("Não entendi.")

        except sr.RequestError:
            print("Erro no serviço de reconhecimento.")

    return ""