import pandas as pd

def convert_excel_to_csv(input_path, output_path):
    # 读取Excel文件
    df = pd.read_excel(input_path)
    
    # 保存为CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"成功将 {input_path} 转换为 {output_path}")

if __name__ == "__main__":
    input_file = "近代史题库.xlsx"
    output_file = "questions.csv"
    convert_excel_to_csv(input_file, output_file)
