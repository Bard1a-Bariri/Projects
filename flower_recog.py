import io
import json
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
import urllib.request
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Flower Classifier", page_icon="🌸")
st.title("🌸 Flower Identifier")
st.write("Upload a flower image or paste an image URL to classify it using PyTorch!")

@st.cache_resource
def load_model():
    model = models.resnet18()
    model.fc = nn.Linear(model.fc.in_features, 102)
    model.load_state_dict(torch.load("flower_model.pth", map_location=torch.device("cpu")))
    model.eval()
    return model

@st.cache_data
def load_categories():
    with open("cat_to_name.json", "r") as f:
        return json.load(f)

model = load_model()
cat_to_name = load_categories()

transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

input_mode = st.radio("Select input method:", ("Upload File", "Paste Image URL"))

pil_img = None

if input_mode == "Upload File":
    uploaded_file = st.file_uploader("Choose a photo...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        pil_img = Image.open(uploaded_file)

else:
    url_input = st.text_input("Enter direct image URL:").strip()
    if url_input:
        try:
            req = urllib.request.Request(url_input, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                pil_img = Image.open(io.BytesIO(response.read()))
        except Exception as e:
            st.error(f"Could not load image from URL: {e}")

if pil_img is not None:

    st.image(pil_img, caption="Input Image", use_container_width=True)

    if st.button("Classify Flower"):
        with st.spinner("Analyzing flower..."):
            pil_con = pil_img.convert("RGB")
            image_tensor = transform(pil_con).unsqueeze(0)

            with torch.no_grad():
                output = model(image_tensor)
                _, predicted_tensor = torch.max(output, dim=1)
                predicted_id = predicted_tensor.item()

            predicted_key = str(predicted_id + 1)
            flower_name = cat_to_name.get(predicted_key, "Unknown Class")

        st.success(f"**Predicted Flower Name:** {flower_name.title()}")