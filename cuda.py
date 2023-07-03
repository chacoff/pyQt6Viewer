import torch

print(f'is cuda available: {torch.cuda.is_available()}')
print(f'how many devices: {torch.cuda.device_count()}')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
current_device = torch.cuda.current_device()
print('Using device:', device)

if device.type == 'cuda':
    print(torch.cuda.get_device_name(current_device))
    print('Memory Usage:')
    print('Allocated:', round(torch.cuda.memory_allocated(current_device)/1024**3,1), 'GB')
    print('Cached:   ', round(torch.cuda.memory_reserved(current_device)/1024**3,1), 'GB')