from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import os
import time

# 定义事件处理器
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, source_dir, destination_dir):
        self.source_dir = source_dir
        self.destination_dir = destination_dir

    def on_modified(self, event):
        # 如果文件被修改，则同步到目标文件夹
        if event.is_directory or 'git' in event.src_path:
            return  # 忽略目录事件，只处理文件事件

        # 获取相对路径并生成目标路径
        relative_path = os.path.relpath(event.src_path, self.source_dir)
        destination_path = os.path.join(self.destination_dir, relative_path)

        # 确保目标文件夹存在
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # 执行同步
        shutil.copy2(event.src_path, destination_path)
        print(f"{time.ctime()}: {event.src_path} 同步到 {destination_path}")

    def on_created(self, event):
        # 如果有新文件或文件夹创建，同步到目标文件夹
        if event.is_directory or 'git' in event.src_path:
            return  # 忽略目录事件

        relative_path = os.path.relpath(event.src_path, self.source_dir)
        destination_path = os.path.join(self.destination_dir, relative_path)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copy2(event.src_path, destination_path)
        print(f"{time.ctime()}: 新文件 {event.src_path} 同步到 {destination_path}")

    def on_deleted(self, event):
        # 如果有文件被删除，在目标文件夹中同步删除
        if event.is_directory or 'git' in event.src_path:
            return  # 忽略目录事件

        relative_path = os.path.relpath(event.src_path, self.source_dir)
        destination_path = os.path.join(self.destination_dir, relative_path)

        if os.path.exists(destination_path):
            os.remove(destination_path)
            print(f"{time.ctime()}: 文件 {destination_path} 已被删除")

    def on_moved(self, event):
        # 如果文件被移动，同步移动到目标文件夹
        if event.is_directory or 'git' in event.src_path:
            return  # 忽略目录事件

        source_relative = os.path.relpath(event.src_path, self.source_dir)
        dest_relative = os.path.relpath(event.dest_path, self.source_dir)

        source_path = os.path.join(self.destination_dir, source_relative)
        destination_path = os.path.join(self.destination_dir, dest_relative)

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
            print(f"{time.ctime()}: 文件 {source_path} 移动到 {destination_path}")

# 源文件夹和目标文件夹路径
source_dir = "/root/VSS"
destination_dir = "/mnt/c/PanoSimDatabase/Plugin/Agent"

# 创建观察器
observer = Observer()
event_handler = FolderChangeHandler(source_dir, destination_dir)
observer.schedule(event_handler, path=source_dir, recursive=True)  # recursive=True 监控子目录

# 开始监控
observer.start()
print(f"开始监控文件夹：{source_dir}")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:

    observer.stop()

observer.join()
