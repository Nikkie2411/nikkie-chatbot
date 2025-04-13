import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1kBkDo4f-bvjPnTMPOl3e8Ebyyuf15KQS"

df = None
embeddings_dict = {}
model = SentenceTransformer('all-MiniLM-L6-v2')
data_load_error = None  # Biến lưu lỗi nếu tải dữ liệu thất bại

def load_data():
    global df, embeddings_dict, data_load_error
    try:
        df = pd.read_csv(GOOGLE_DRIVE_URL, encoding="utf-8-sig")
        print("Loaded data from Google Drive successfully.")
        data_load_error = None  # Reset lỗi nếu tải thành công

        embeddings_dict.clear()
        target_columns = ["2_1lieu_tre_so_sinh", "2_2lieu_tre_em"]
        for column in target_columns:
            if column in df.columns:
                texts = df[column].dropna().astype(str).tolist()
                if texts:
                    embeddings = model.encode(texts, convert_to_tensor=True)
                    embeddings_dict[column] = (texts, embeddings)
    except Exception as e:
        print(f"Error loading data from Google Drive: {e}")
        data_load_error = str(e)

load_data()

def answer_query(query, refresh_data=False):
    global df, embeddings_dict, data_load_error
    try:
        if refresh_data:
            print("Refreshing data...")
            load_data()

        if data_load_error:
            return f"Lỗi tải dữ liệu: {data_load_error}"
        if df is None or not embeddings_dict:
            return "Dữ liệu chưa được tải. Vui lòng thử lại sau."

        query_embedding = model.encode(query, convert_to_tensor=True)
        max_score = -1
        best_match = None
        best_column = None

        for column, (texts, embeddings) in embeddings_dict.items():
            scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]
            max_idx = np.argmax(scores)
            score = scores[max_idx].item()

            if score > max_score and score > 0.5:
                max_score = score
                best_match = texts[max_idx]
                best_column = column

        if best_match:
            return best_match
        else:
            return "Không tìm thấy thông tin phù hợp."
    except Exception as e:
        print(f"Debug - Lỗi xử lý query: {e}")
        return "Lỗi xử lý yêu cầu."