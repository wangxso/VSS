import os

def delete_zone_identifier_files(folder_path):
    # 遍历文件夹及其子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if "Zone.Identifier" in file:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    folder_to_clean = r"/root/VSS"  # 替换为目标文件夹路径
    delete_zone_identifier_files(folder_to_clean)