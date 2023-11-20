import streamlit as st
import pandas as pd
import base64
import requests
import tempfile
from PIL import Image

# Config
st.set_page_config(page_title='EcoLens', page_icon=':recycle:', layout='wide')

st.title('EcoLens')

# Input the number of trash bins
st.subheader('Step 1. Enter Number of Trash Bins')
number_of_bins = st.number_input("How many trash bins do you have?", min_value=1, max_value=10)
st.write("Number of trash bins:", number_of_bins)

# Select the type of trash bins which you can use
st.subheader('Step 2. Select Type of Trash Bins')
bin_types = st.multiselect("Select the type of trash bins you have", ["General Waste", "Plastic", "Glass", "Paper", "Metal", "Organic"])
st.write("Selected trash bin types:", bin_types)


# Image upload
st.subheader('Step 3. Upload Image')
uploaded_file = st.file_uploader("Upload your image here", type=["jpg", "png", "jpeg"])
image_path = None 

if uploaded_file is not None:
    # Save the file to a temporary directory
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.getvalue())

    # Open it with PIL
    image = Image.open(tfile.name)
    st.image(image, caption='Uploaded Image')

    # Set the image path for further use
    image_path = tfile.name


question_templates = {
    "English": "What’s in this image and how do I recycle this object in {}? I have {} trash bins available. Types: {}.",
    "Korean": "이 이미지에 무엇이 있고, {}에서 이 물건을 어떻게 재활용하나요? 사용 가능한 쓰레기통은 {}개 있습니다. 종류: {}.",
    "Japanese": "この画像には何がありますか、また{}ではこのオブジェクトをどのようにリサイクルしますか？使用可能なゴミ箱は{}個あります。種類: {}。",
    "Chinese": "这张图片里有什么，我该如何在{}回收这个物品？我有{}个可用的垃圾桶。类型: {}。",
    "German": "Was ist auf diesem Bild und wie recycelt man dieses Objekt in {}? Ich habe {} Mülleimer zur Verfügung. Arten: {}.",
    "French": "Que contient cette image et comment puis-je recycler cet objet en {}? J'ai {} poubelles disponibles. Types: {}.",
    "Others": "What’s in this image and how do I recycle this object in {}? I have {} trash bins available. Types: {}."
}

# Select languages
st.subheader('Step 4. Select Language')
selected_language = st.selectbox("Choose your language", list(question_templates.keys()))
st.write("Selected language:", selected_language)

# Country selection
st.subheader('Step 5. Select Country')
country = st.selectbox("Choose your country", ["South Korea", "USA", "Japan", "China", "Germany", "France", "Others"])
st.write("Selected country:", country)

# Customize the question based on the selected country
question_text = question_templates[selected_language].format(country, number_of_bins, ', '.join(bin_types))

# Check if an image was uploaded before proceeding
if image_path:
    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # OpenAI API Key
    api_key = "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"

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": question_text
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        st.write(content)
    else:
        st.error(f"Error: {response.status_code}")