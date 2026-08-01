import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms 
import torchvision.models as models         
import torchvision.datasets as datasets

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
  transforms.Resize((224, 224)),
  transforms.ToTensor(),
  transforms.Normalize(
    mean=[0.485, 0.456, 0.406], 
    std=[0.229, 0.224, 0.225]
    )
])

train_set = datasets.Flowers102(
  root="./d",
  split='train',
  download=True,
  transform=transform
  )
  
train_loader = Dataloader(train_set, batch_size=16, shuffle=True)
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

for p in parameters():
  p.requires_grad = False

num_features = model.fc.in_featurs
model.fc = nn.Linear(num_features, 102)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

model.train()
running_loss = 0

for idx, (image, label) in enumerate(train_loader):
  images, labels = image.to(devices), label.to(device)
  
  outputs = model(images)
  loss = criterion(outputs, label)
  optimizer.zero_grad()
  loss.backward()
  optimizer.step()
  
  running_loss += loss.item()
  
  if (idx+1) % 10 == 0:
    print(f"Batch [{batch_idx + 1}/{len(train_loader)}] ── Loss: {loss.item():.4f}")
    