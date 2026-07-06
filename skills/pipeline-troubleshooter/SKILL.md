# Pipeline Troubleshooter — GPU/CUDA/ML Environment Debugging

**Domain:** AI Pipelines / GPU Compute / Python Environments
**Author:** Gaya (deployed for R0n, 30-May-2026)

---

## When to Use

Activate when the user encounters:
- **CUDA errors** — `CUDA error: out of memory`, `CUDA driver version insufficient`, `CUDA error: device-side assert`
- **VAE mismatches** — `size mismatch`, tensor shape errors in ComfyUI/Stable Diffusion
- **Conda/Python environment issues** — `PATH error`, package conflicts, missing modules
- **ComfyUI errors** — node errors, model load failures, workflow crashes
- **LLM inference issues** — model load fails, wrong model path, quantization errors
- **General GPU pipeline failures** — any pipeline tool stops working

## NOT for
- Game engine errors (UE5 — use `unreal-engine-cpp-pro`)
- Web development errors
- Hardware purchase advice

---

## Diagnostic Workflow

### Step 1: Identify the Error Type

| Error Pattern | Likely Root | Debug Command |
|---|---|---|
| `CUDA error: out of memory` | VRAM full, batch too large | `nvidia-smi`, check VRAM usage |
| `CUDA driver version is insufficient` | Wrong CUDA toolkit version | `nvidia-smi`, `nvcc --version` |
| `size mismatch` | Model weights vs architecture | Check model file, checkpoint, LoRA size |
| `reshape error` | Input tensor wrong shape | Check image size, batch dimension |
| `No module named 'X'` | Missing dependency | `pip install X` |
| `CondaPathError` / PATH issues | Conda not in PATH | `where conda`, check env vars |
| `GGUF` / model load failure | Wrong model path or corrupt file | Check file exists, hash verify |

### Step 2: Common Fixes (Try in Order)

#### CUDA Out of Memory
```bash
nvidia-smi                          # Check what's using VRAM
taskkill /F /IM python.exe          # Kill orphaned processes
# Then reduce batch size or model size
```

#### CUDA Driver Version
```bash
nvidia-smi                          # Shows driver version + CUDA version
nvcc --version                      # Shows CUDA toolkit version
# Match driver to toolkit: https://docs.nvidia.com/deploy/cuda-compatibility/
```

#### VAE/Model Size Mismatch
```
"This VAE is not compatible with this model"
→ Check model is SD1.5/SDXL/Flux — VAE must match base model
→ LoRA/Checkpoint was trained on different base
→ Solution: download correct VAE for the model architecture
```

#### Conda PATH Error (Windows)
```powershell
# Conda not recognized
where conda                        # Check if installed
$env:Path += ";C:\Users\<user>\miniconda3\Scripts"
conda init powershell              # Fix PATH permanently
```

#### ComfyUI Node Errors
```
1. Check node manager updates
2. Reinstall problem nodes
3. Check workflow JSON for missing node types
4. Verify model files in correct ComfyUI/models/ subdirectory
```

### Step 3: Environment Health Check

```powershell
# Python + pip
python --version
pip --version
pip list | findstr torch          # Check PyTorch version
pip list | findstr cuda           # Check CUDA packages

# GPU
nvidia-smi
# Look for: CUDA Version, GPU-Util, Memory-Usage

# Conda (if using)
conda info --envs
conda list | findstr cuda
```

### Step 4: If Still Broken → Reset

Sometimes the fastest path is:
```powershell
conda deactivate
conda remove --name myenv --all
conda create -n myenv python=3.10
conda activate myenv
pip install -r requirements.txt
```

Or for venv:
```powershell
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## Error Database (Evergreen)

| Error | Root Cause | Quick Fix |
|---|---|---|
| `CUDA OOM` | VRAM exhausted | Reduce batch size, close other apps, use smaller model |
| `CUDA driver insufficient` | Driver too old for toolkit | Update NVIDIA driver OR install compatible CUDA toolkit |
| `VAE size mismatch` | Wrong VAE for SD version | Download correct VAE for SD1.5/SDXL/Flux |
| `reshape error` | Wrong image dimensions | Ensure input is divisible by 8, correct channels |
| `module not found` | Missing package | `pip install [module]` |
| `FileNotFoundError` on model | Wrong path | Check file exists, update config path |
| `GGUF` load failure | Corrupt/incompatible GGUF | Re-download, check q4_k_m vs q8_0 variants |
| `Failed to create process` | Python or path issue | Reinstall Python, check PATH |

---

## RTX 5090 Specific Notes

- Latest driver required (572.x+)
- CUDA 12.8+ recommended
- 32GB VRAM — can run SDXL + Flux at high resolution
- Watch for PCIe bandwidth bottlenecks if using PCIe 4.0 x8
- ComfyUI: add `--highvram` flag for full 32GB utilization
