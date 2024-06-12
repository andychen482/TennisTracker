import torch

# verify cuda
print(torch.cuda.is_available())
print(torch.cuda.device_count())