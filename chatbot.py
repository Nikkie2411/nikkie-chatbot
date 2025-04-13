from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import re
import unicodedata

# Tải dữ liệu
try:
    df = pd.read_csv("thuoc_data.csv", encoding="utf-8-sig")
    print("Debug - Đọc thuoc_data.csv thành công")
except Exception as e:
    print(f"Debug - Lỗi đọc thuoc_data.csv: {e}")
    df = pd.DataFrame()  # Để tránh lỗi nếu CSV không tồn tại

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Danh sách từ khóa cho Heading 1
FIELD_KEYWORDS = {
    "1phan_loai": ["phân loại", "loại thuốc", "nhóm thuốc"],
    "2_1lieu_tre_so_sinh": ["liều trẻ sơ sinh", "liều sơ sinh", "trẻ sơ sinh"],
    "2_2lieu_tre_em": ["liều trẻ em", "trẻ em", "liều nhi"],
    "2_3hieu_chinh_than": ["hiệu chỉnh thận", "chức năng thận", "suy thận"],
    "2_4hieu_chinh_gan": ["hiệu chỉnh gan", "chức năng gan", "suy gan"],
    "3chong_chi_dinh": ["chống chỉ định", "không dùng", "kiêng kỵ"],
    "4tdkmm_thantrong": ["tác dụng phụ", "tác dụng không mong muốn", "thận trọng"],
    "5cach_dung": ["cách dùng", "cách sử dụng", "dùng thuốc", "đường uống", "đường tiêm"],
    "6tuong_tac": ["tương tác", "tương tác thuốc"],
    "7qua_lieu": ["quá liều", "liều cao"],
    "8theo_doi_dieu_tri": ["theo dõi", "giám sát", "điều trị"],
    "9bhyt": ["bảo hiểm", "bảo hiểm y tế", "thanh toán bhyt"]
}

def normalize_text(text):
    """Chuẩn hóa chuỗi: bỏ dấu, chữ thường, bỏ khoảng trắng thừa."""
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^\w_]', '', text)
    return text

def identify_field_and_heading2(query, columns):
    """Xác định trường Heading 1 và Heading 2 từ câu hỏi."""
    query_normalized = normalize_text(query)
    print(f"Debug - Query normalized: {query_normalized}")
    field = None
    heading2 = None
    best_h2_score = 0
    best_h2_col = None

    for field_key, keywords in FIELD_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in query_normalized:
                field = field_key
                print(f"Debug - Field matched: {field_key}")
                break
        if field:
            break

    if field:
        for col in columns:
            if col.startswith(field + "_"):
                h2_key = col[len(field) + 1:]
                h2_normalized = normalize_text(h2_key)
                print(f"Debug - Checking Heading 2: {h2_key} -> {h2_normalized}")
                if h2_normalized in query_normalized:
                    heading2 = col
                    print(f"Debug - Heading 2 matched (exact): {heading2}")
                    break
                common_chars = len(set(h2_normalized) & set(query_normalized))
                score = common_chars / max(len(h2_normalized), 1)
                if score > best_h2_score and score > 0.5:
                    best_h2_score = score
                    best_h2_col = col
                    print(f"Debug - Heading 2 candidate: {col} (score: {score})")

        if not heading2 and best_h2_col:
            heading2 = best_h2_col
            print(f"Debug - Heading 2 selected (fuzzy): {heading2}")

    return field, heading2

def answer_query(query):
    if df.empty:
        return "Không thể đọc dữ liệu thuốc."

    query_embedding = model.encode(query, convert_to_tensor=True)
    drug_info = df["ten_thuoc"].tolist()
    embeddings = model.encode(drug_info, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, embeddings)[0]
    best_idx = np.argmax(similarities).item()
    print(f"Debug - Drug matched: {drug_info[best_idx]} (score: {similarities[best_idx]})")

    if similarities[best_idx] < 0.5:
        return "Không tìm thấy thông tin phù hợp."

    drug_row = df.iloc[best_idx]
    drug_name = drug_row["ten_thuoc"]

    field, heading2 = identify_field_and_heading2(query, df.columns)

    if heading2:
        value = drug_row[heading2]
        if pd.isna(value) or value.strip() == "":
            print(f"Debug - Không có dữ liệu cho cột: {heading2}")
            return "Không có thông tin phù hợp."
        print(f"Debug - Trả về Heading 2: {heading2} = {value}")
        return str(value)  # Chỉ trả về nội dung cột
    elif field:
        value = drug_row[field]
        if pd.isna(value) or value.strip() == "":
            print(f"Debug - Không có dữ liệu cho cột: {field}")
            return "Không có thông tin phù hợp."
        print(f"Debug - Trả về Heading 1: {field} = {value}")
        return str(value)  # Chỉ trả về nội dung cột
    else:
        # Nếu không xác định field, trả về thông tin tổng quát
        print(f"Debug - Không xác định field, trả về thông tin tổng quát")
        for col in df.columns:
            if col != "ten_thuoc" and not pd.isna(drug_row[col]) and drug_row[col].strip():
                value = drug_row[col]
                print(f"Debug - Kiểm tra cột tổng quát: {col} = {value}")
                if normalize_text(query) in normalize_text(col) or normalize_text(query) in normalize_text(value):
                    return str(value)  # Trả về cột khớp nhất
        return "Không tìm thấy thông tin phù hợp."
