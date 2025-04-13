import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load dữ liệu
df = pd.read_csv("thuoc_data.csv", encoding="utf-8-sig")

# Load mô hình nhẹ hơn
model = SentenceTransformer('all-MiniLM-L6-v2')

# Tạo embeddings cho các cột
embeddings_dict = {}
for column in df.columns[1:]:  # Bỏ cột đầu tiên (tên thuốc)
    texts = df[column].dropna().astype(str).tolist()
    if texts:
        embeddings = model.encode(texts, convert_to_tensor=True)
        embeddings_dict[column] = (texts, embeddings)

def answer_query(query):
    try:
        query_embedding = model.encode(query, convert_to_tensor=True)
        max_score = -1
        best_match = None
        best_column = None

        for column, (texts, embeddings) in embeddings_dict.items():
            scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]
            max_idx = np.argmax(scores)
            score = scores[max_idx].item()

            if score > max_score and score > 0.5:  # Ngưỡng 0.5 để đảm bảo độ chính xác
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