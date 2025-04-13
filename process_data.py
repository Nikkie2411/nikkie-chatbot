from bs4 import BeautifulSoup
import pandas as pd
import re
import os

def extract_text_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        text = []
        current_heading1 = ""
        current_heading2 = ""

        # Duyệt qua các thẻ h, h1, h2, p
        for element in soup.find_all(['h', 'h1', 'h2', 'p']):
            tag_name = element.name
            content = element.get_text(strip=True)
            if not content:
                continue

            print(f"Debug - Tag: {tag_name}, Content: {content}")

            if tag_name == 'h':
                # Tên thuốc, không set heading1
                text.append(("", "", content))
            elif tag_name == 'h1':
                current_heading1 = content
                current_heading2 = ""
                text.append((current_heading1, "", content))
            elif tag_name == 'h2' and current_heading1:
                current_heading2 = content
                text.append((current_heading1, current_heading2, content))
            elif tag_name == 'p' and current_heading1:
                text.append((current_heading1, current_heading2, content))

        return text
    except Exception as e:
        print(f"Lỗi khi đọc {file_path}: {e}")
        return []

def parse_drug_data(text_lines, file_name):
    current_drug = {
        "ten_thuoc": "",
        "1phan_loai": [],
        "2_1lieu_tre_so_sinh": {"_content": []},
        "2_2lieu_tre_em": {"_content": []},
        "2_3hieu_chinh_than": [],
        "2_4hieu_chinh_gan": [],
        "3chong_chi_dinh": [],
        "4tdkmm_thantrong": {"_content": []},
        "5cach_dung": {"_content": []},
        "6tuong_tac": {"_content": []},
        "7qua_lieu": [],
        "8theo_doi_dieu_tri": {"_content": []},
        "9bhyt": [],
    }

    HEADING2_FIELDS = [
        "2_1lieu_tre_so_sinh",
        "2_2lieu_tre_em",
        "4tdkmm_thantrong",
        "5cach_dung",
        "6tuong_tac",
        "8theo_doi_dieu_tri",
    ]

    heading1_key_map = {
        "1. Phân loại dược lý": "1phan_loai",
        "2.1. Liều thông thường trẻ sơ sinh": "2_1lieu_tre_so_sinh",
        "2.2. Liều thông thường trẻ em": "2_2lieu_tre_em",
        "2.3. Hiệu chỉnh liều theo chức năng thận": "2_3hieu_chinh_than",
        "2.4. Hiệu chỉnh liều theo chức năng gan": "2_4hieu_chinh_gan",
        "3. Chống chỉ định": "3chong_chi_dinh",
        "4. Tác dụng không mong muốn điển hình và thận trọng": "4tdkmm_thantrong",
        "5. Cách dùng": "5cach_dung",
        "6. Tương tác thuốc": "6tuong_tac",
        "7. Quá liều": "7qua_lieu",
        "8. Theo dõi điều trị": "8theo_doi_dieu_tri",
        "9. Bảo hiểm y tế thanh toán": "9bhyt",
    }

    for heading1, heading2, line in text_lines:
        print(f"Debug - Processing: H1='{heading1}', H2='{heading2}', Line='{line}'")

        # Lấy tên thuốc từ thẻ <h>
        if not current_drug["ten_thuoc"] and heading1 == "" and heading2 == "":
            current_drug["ten_thuoc"] = line
            print(f"Debug - Stored ten_thuoc: {line}")
            continue

        # Tìm key cho Heading 1
        heading1_key = None
        for h1_pattern, h1_key in heading1_key_map.items():
            if heading1.startswith(h1_pattern):
                heading1_key = h1_key
                break

        if heading1_key:
            if heading2 and heading1_key in HEADING2_FIELDS:
                heading2_key = re.sub(r'\s+', '_', heading2.lower())
                heading2_key = re.sub(r'[^\w]', '', heading2_key)
                if heading2_key not in current_drug[heading1_key]:
                    current_drug[heading1_key][heading2_key] = []
                current_drug[heading1_key][heading2_key].append(line)
                current_drug[heading1_key]["_content"].append(line)
                print(f"Debug - Stored H2: {heading1_key}.{heading2_key} = {line}")
            else:
                # Lưu nội dung Heading 1
                if isinstance(current_drug[heading1_key], list):
                    current_drug[heading1_key].append(line)
                    print(f"Debug - Stored H1: {heading1_key} = {line}")
                elif heading1_key in HEADING2_FIELDS:
                    current_drug[heading1_key]["_content"].append(line)
                    print(f"Debug - Stored H1 content: {heading1_key}._content = {line}")
                else:
                    current_drug[heading1_key].append(line)
                    print(f"Debug - Stored H1: {heading1_key} = {line}")

    print(f"Debug - Final current_drug: {current_drug}")
    return current_drug

def process_all_docx_files(directory):
    drug_dict = {}

    for file_name in os.listdir(directory):
        if file_name.endswith(".html") and not file_name.startswith("~$"):
            print(f"Đang xử lý: {file_name}")
            file_path = os.path.join(directory, file_name)
            text_lines = extract_text_from_html(file_path)
            if text_lines:
                current_drug = parse_drug_data(text_lines, file_name)
                if current_drug["ten_thuoc"]:
                    drug_name = current_drug["ten_thuoc"]
                    drug_dict[drug_name] = {}
                    
                    # Gộp Heading 1 và Heading 2
                    for key, value in current_drug.items():
                        if key == "ten_thuoc":
                            continue
                        if isinstance(value, list) and value:
                            drug_dict[drug_name][key] = "\n".join(value)
                            print(f"Debug - Added Heading 1 to drug_dict: {drug_name}, Column: {key}, Content: {drug_dict[drug_name][key]}")
                        elif isinstance(value, dict):
                            # Lưu nội dung Heading 1 từ _content
                            if "_content" in value and value["_content"]:
                                drug_dict[drug_name][key] = "\n".join(value["_content"])
                                print(f"Debug - Added Heading 1 to drug_dict: {drug_name}, Column: {key}, Content: {drug_dict[drug_name][key]}")
                            # Gộp Heading 2
                            for h2_key, h2_content in value.items():
                                if h2_key == "_content":
                                    continue
                                col_name = f"{key}_{h2_key}"
                                drug_dict[drug_name][col_name] = "\n".join(h2_content)
                                print(f"Debug - Added Heading 2 to drug_dict: {drug_name}, Column: {col_name}, Content: {drug_dict[drug_name][col_name]}")

    # Chuyển drug_dict thành all_data
    all_data = {
        "ten_thuoc": [],
        "1phan_loai": [],
        "2_1lieu_tre_so_sinh": [],
        "2_2lieu_tre_em": [],
        "2_3hieu_chinh_than": [],
        "2_4hieu_chinh_gan": [],
        "3chong_chi_dinh": [],
        "4tdkmm_thantrong": [],
        "5cach_dung": [],
        "6tuong_tac": [],
        "7qua_lieu": [],
        "8theo_doi_dieu_tri": [],
        "9bhyt": [],
    }

    # Thu thập tất cả cột Heading 2
    for drug_name, drug_info in drug_dict.items():
        for key in drug_info:
            if key not in all_data:
                all_data[key] = []

    # Điền dữ liệu vào all_data, mỗi thuốc 1 dòng
    for drug_name, drug_info in drug_dict.items():
        all_data["ten_thuoc"].append(drug_name)
        for key in all_data:
            if key == "ten_thuoc":
                continue
            value = drug_info.get(key, "")
            all_data[key].append(value)
            print(f"Debug - Added to all_data: Drug: {drug_name}, Column: {key}, Value: {value}")

    df = pd.DataFrame(all_data)
    df.to_csv("thuoc_data.csv", index=False, encoding="utf-8-sig")
    print("Dữ liệu tất cả thuốc đã lưu vào thuoc_data.csv")

if __name__ == "__main__":
    process_all_docx_files(".")