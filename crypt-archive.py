import os
import subprocess
import datetime
import shutil


def backup_folders(source_folder, destination_folder):
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
            if os.path.exists(os.path.join(user_path,post)):
                print(f'{post} 已备份!')
            else:
                shutil.copytree(str(os.path.join(source_folder, user, post)),str(os.path.join(destination_folder, user, post))) 
                print(f'{post} 备份完成!')   
        json_name = f'{user}.json'
        shutil.copy(f'./{json_name}', f'{destination_folder}/{json_name}')

if __name__ == "__main__":
    # 指定源文件夹、目标文件夹和密码
    source_folder = "./Downloads"
    destination_folder = "/webdav/Crypt/Aliyundrive/coomer"

    # 调用备份函数
    backup_folders(source_folder, destination_folder)

