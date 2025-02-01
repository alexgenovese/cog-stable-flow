# Stable Flow – Cog Model for Image Editing

This repository provides a configuration to run the "Stable Flow" model (based on the official [snap-research/stable-flow](https://github.com/snap-research/stable-flow) repository) as a Cog model. The configuration includes:

- **Automatic download** of the repository and the necessary weights (using [pget](https://github.com/Code-Hex/pget) for faster downloading) during the setup phase.
- Execution of the `run_stable_flow.py` script with parameters passed via the `predict()` function.
- Handling of editing prompts and (optionally) an input image.

> **Note:** The setup function checks if the `stable-flow` folder and the weights file (e.g. `weights.pth`) exist. If not, it clones the repository and downloads the weights from Hugging Face. For authenticated downloads, the HF token must be provided via the `HF_TOKEN` environment variable.

---

## Prerequisites

- **Docker**: Required to run Cog.
- **Cog**: Install following the official instructions (e.g. via `curl`).
- **pget**: A tool to download files faster.  
  Install it (if not already installed) with:
  ```bash
  pip install pget

Set the Hugging Face token by exporting the HF_TOKEN environment variable:
```
export HF_TOKEN=your_huggingface_token
```

# File Structure
**cog.yaml** Defines the build environment (Python version, dependencies, etc.) and specifies predict.py as the prediction interface.
**predict.py** Contains the Predictor class that, in the setup() method, downloads the stable-flow repository and weights (using pget with authentication via HF_TOKEN), and in the predict() method executes the run_stable_flow.py script with the provided parameters.

# Running Locally
## 1. Environment Setup
- Ensure Docker and Cog are installed.
- Install pget if it isn’t already:
```
pip install pget
```

- Set the Hugging Face token:
```
export HF_TOKEN=your_huggingface_token
```

## 2. Running the Model
From the project root (where cog.yaml and predict.py reside), run:
```
cog predict -i prompts='["Original prompt", "Edit prompt 1", "Edit prompt 2"]'
```

If you want to use an input image for real image editing, add the image parameter:
```
cog predict -i prompts='["Image description", "Edit description..."]' -i input_img=@/path/to/image.jpg
```

During setup, the code will check (and download, if necessary) the stable-flow repository and the weights. The inference is executed via the run_stable_flow.py script, and the output is saved to stable-flow/outputs/result.jpg.