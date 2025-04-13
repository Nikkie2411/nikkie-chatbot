import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import os
import torch
import requests
from io import BytesIO

os.environ["TOKENIZERS_PARALLELISM"] = "false"

GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1kBkDo4f-bvjPnTMPOl3e8Ebyyuf15KQS"
EMBEDDINGS_URL = "https://drive.google.com/uc?export=download&id=1NuqCXDLygPQQZ9mVckFeM_QseDwvUhQj"

df = None
embeddings_dict = {}
model = None
data_load_error = None

def initialize_model():
    global model
    if model is None:
        print("Initializing SentenceTransformer model...")
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model initialized successfully.")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise

def load_embeddings():
    global embeddings_dict
    try:
        response = requests.get(EMBEDDINGS_URL)
        embeddings_dict = torch.load(BytesIO(response.content))
        print("Loaded embeddings from Google Drive successfully.")
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return False
    return True

def load_data():
    global df, embeddings_dict, data_load_error
    try:
        print("Loading data from Google Drive...")
        df = pd.read_csv(GOOGLE_DRIVE_URL, encoding="utf-8-sig")
        print("Loaded data from Google Drive successfully.")
        data_load_error = None

        # Tải embeddings từ file
        if not load_embeddings():
            print("Creating embeddings as fallback...")
            embeddings_dict.clear()
            target_columns = ["2_1lieu_tre_so_sinh", "2_2lieu_tre_em"]
            for column in target_columns:
                if column in df.columns:
                    texts = df[column].dropna().astype(str).tolist()
                    if texts:
                        print(f"Creating embeddings for column: {column}")
                        initialize_model()
                        embeddings = model.encode(texts, convert_to_tensor=True)
                        embeddings_dict[column] = (texts, embeddings)
                        print(f"Embeddings created for column: {column}")
                else:
                    print(f"Column {column} not found in data.")

            # Lưu embeddings vào file
            save_embeddings()
    except Exception as e:
        print(f"Error loading data from Google Drive: {e}")
        data_load_error = str(e)

def save_embeddings():
    global embeddings_dict
    try:
        embeddings_path = os.path.join(os.getcwd(), "embeddings.pt")
        print(f"Saving embeddings to: {embeddings_path}")
        torch.save(embeddings_dict, embeddings_path)
        print(f"Saved embeddings to {embeddings_path}. Please upload to Google Drive and update EMBEDDINGS_URL.")
    except Exception as e:
        print(f"Error saving embeddings: {e}")
        raise

# Chạy load_data() để tạo embeddings.pt
if __name__ == "__main__":
    print("Starting to create embeddings.pt...")
    load_data()
    if data_load_error:
        print(f"Failed to create embeddings.pt: {data_load_error}")
    else:
        print("Done creating embeddings.pt.")