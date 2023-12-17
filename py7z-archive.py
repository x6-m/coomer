import os
import subprocess
import datetime
import shutil


def backup_folders(source_folder, destination_folder, password):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 '{source_folder}' 不存在.")
        return
    
    users = os.listdir(source_folder)
    for user in users:
        user_path = os.path.join(destination_folder, user)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        
        posts = os.listdir(os.path.join(source_folder, user))
        for post in posts:
            backup_filename = f'{post}_pwd={password}.7z'
            if os.path.exists(os.path.join(user_path,backup_filename)):
                print(f'{backup_filename} 已备份!')
            else:
                try:
                    command = ["7z", "a", "-p" + password, os.path.join(user_path,backup_filename), os.path.join(source_folder, user, post)]
                    subprocess.run(command, check=True)
                    print(f"成功将文件夹压缩到 {backup_filename}")
                except subprocess.CalledProcessError as e:
                    print(f"压缩失败: {e}")        
        json_name = f'{user}.json'
        shutil.copy(f'./{json_name}', f'{destination_folder}/{json_name}')

if __name__ == "__main__":
    # 指定源文件夹、目标文件夹和密码
    source_folder = "./Downloads"
    destination_folder = "/webdav/Aliyundrive/archive/coomer"
    password = "x6-m.eu.org"

    # 调用备份函数
    backup_folders(source_folder, destination_folder, password)

