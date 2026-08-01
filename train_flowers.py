import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torchvision.models as models

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"⚙️ Using device: {device}")

# 2. Transforms & Data Loading
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("Downloading/Loading Flowers102 Dataset...")
train_dataset = datasets.Flowers102(root="./data", split="train", download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True)
print(f"Dataset loaded! Total batches: {len(train_loader)}")

print("Loading ResNet18 model weights...")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 102)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)


print("\nStarting Training...")
model.train()
num_epochs = 10

for epoch in range(num_epochs):
    running_loss = 0.0
    
    for batch_idx, (images, labels) in enumerate(train_loader, start=1):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Batch [{batch_idx}/{len(train_loader)}] - Loss: {loss.item():.4f}")

    print(f"Epoch {epoch + 1} Complete! Average Loss: {running_loss / len(train_loader):.4f}\n")

torch.save(model.state_dict(), "flower_model.pth")
print("SUCCESS! Saved trained weights to 'flower_model.pth'")