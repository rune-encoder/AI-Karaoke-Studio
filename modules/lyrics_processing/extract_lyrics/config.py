import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "int8_float16" if DEVICE == "cuda" else "int8"
MODEL_SIZE = "large-v3"