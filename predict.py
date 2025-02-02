import os
import subprocess
from typing import List
from cog import BasePredictor, Input, Path

def download_repo_and_weights():
    # Check if the "stable-flow" folder exists; if not, clone the repository.
    if not os.path.exists("stable-flow"):
        print("Cloning the stable-flow repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/snap-research/stable-flow.git"],
            check=True
        )
    else:
        print("stable-flow repository already exists.")
    
    # Define the path for the weights file (adjust filename if needed)
    weights_path = os.path.join("stable-flow", "weights.pth")
    if not os.path.exists(weights_path):
        print("Downloading required weights with pget...")
        # URL of the weights (modify as needed)
        weights_url = "https://huggingface.co/snap-research/stable-flow/resolve/main/weights.pth"
        # Retrieve the HF token from the environment variable
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token is None:
            raise Exception("Please set the HF_TOKEN environment variable to download the weights.")
        
        # Build the pget command including the authorization header.
        download_cmd = [
            "pget",
            "-H", f"Authorization: Bearer {hf_token}",
            "-o", weights_path,
            weights_url
        ]
        subprocess.run(download_cmd, check=True)
    else:
        print("Weights already present.")

class Predictor(BasePredictor):
    def setup(self):
        """
        Setup ensures that the stable-flow repository and its weights are available.
        If they are missing, the repository is cloned and the weights are downloaded.
        """
        download_repo_and_weights()

    def predict(
        self,
        prompt_1: str = Input(
            description="Prompt describing the original scene.",
            default="A photo of a dog in standing the street",
        ),
        prompt_2: str = Input(
            description="Prompt describing the edited scene.",
            default="A photo of a dog sitting in the street",
        ),
        input_img: str = Input(
            description="(Optional) Path to the input image for real image editing. Leave empty if not provided.",
            default="",
        )
    ) -> Path:
        """
        Executes the run_stable_flow.py script (located in the cloned repository)
        using the provided prompts and optional input image. The output is saved to
        stable-flow/outputs/result.jpg.
        """
        # Combine the two prompts into a list.
        prompts = [prompt_1, prompt_2]

        # Build the command to run the inference script.
        command = [
            "python", "run_stable_flow.py",
            "--prompts"
        ] + prompts

        # If an input image path is provided, add it to the command.
        if input_img.strip():
            command += ["--input_img_path", input_img.strip()]

        # Set cpu_offload to False by default (no flag is appended).

        # Specify the output file path (relative to the stable-flow directory).
        output_file = os.path.join("outputs", "result.jpg")
        command += ["--output_path", output_file]

        # Ensure the outputs directory exists within the stable-flow folder.
        outputs_dir = os.path.join("stable-flow", "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        # Run the script in the stable-flow directory.
        subprocess.run(command, cwd="stable-flow", check=True)

        # Return the path to the resulting image.
        return Path(os.path.join("stable-flow", output_file))
