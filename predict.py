import os
import subprocess
from typing import List, Optional
from cog import BasePredictor, Input, Path

def download_repo_and_weights():
    # Verifica la presenza della cartella "stable-flow" e clona il repository se non esiste.
    if not os.path.exists("stable-flow"):
        print("Clonazione del repository stable-flow...")
        subprocess.run(
            ["git", "clone", "https://github.com/snap-research/stable-flow.git"],
            check=True
        )
    else:
        print("Repository stable-flow già presente.")
    
    # Definisce il percorso dei pesi (modifica il nome del file se necessario).
    weights_path = os.path.join("stable-flow", "weights.pth")
    if not os.path.exists(weights_path):
        print("Scaricamento dei pesi necessari con pget...")
        # URL dei pesi (modifica se necessario)
        weights_url = "https://huggingface.co/snap-research/stable-flow/resolve/main/weights.pth"
        # Recupera il token di Hugging Face dalla variabile d'ambiente
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token is None:
            raise Exception("Devi impostare la variabile d'ambiente HF_TOKEN per scaricare i pesi.")
        
        # Costruisce il comando per pget includendo l'header di autorizzazione.
        download_cmd = [
            "pget",
            "-H", f"Authorization: Bearer {hf_token}",
            "-o", weights_path,
            weights_url
        ]
        subprocess.run(download_cmd, check=True)
    else:
        print("Pesi già presenti.")

class Predictor(BasePredictor):
    def setup(self):
        """
        La funzione di setup verifica la presenza del repository stable-flow e dei pesi.
        Se non sono presenti, li scarica (usando pget per i pesi, con autenticazione tramite HF_TOKEN).
        """
        download_repo_and_weights()

    def predict(
        self,
        prompts: List[str] = Input(
            description=("Lista di prompt: il primo descrive la scena originale, "
                         "mentre i successivi definiscono le modifiche da applicare."),
        ),
        input_img: Optional[Path] = Input(
            description="(Opzionale) Immagine di input per editing su immagine reale.",
            default=None,
        ),
        cpu_offload: bool = Input(
            description="Abilita CPU offloading se necessario per GPU con poca VRAM",
            default=False,
        )
    ) -> Path:
        """
        Esegue lo script run_stable_flow.py (presente nella cartella clonata) con i parametri indicati.
        L’output viene salvato in stable-flow/outputs/result.jpg.
        """
        # Costruisco la lista dei comandi per eseguire lo script.
        command = [
            "python", "run_stable_flow.py",
            "--prompts"
        ] + prompts

        if input_img is not None:
            command += ["--input_img_path", str(input_img)]

        if cpu_offload:
            command.append("--cpu_offload")

        # Definisce il percorso di output (all'interno della cartella stable-flow)
        output_file = os.path.join("outputs", "result.jpg")
        command += ["--output_path", output_file]

        # Assicura l'esistenza della cartella outputs all'interno del repository
        outputs_dir = os.path.join("stable-flow", "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        # Esegue lo script nella directory del repository stable-flow
        subprocess.run(command, cwd="stable-flow", check=True)

        # Restituisce il percorso dell'immagine risultante
        return Path(os.path.join("stable-flow", output_file))
