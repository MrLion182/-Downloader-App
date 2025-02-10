import requests

def download_file(url, save_path):
    """
    下载文件到指定路径

    :param url: 文件 URL
    :param save_path: 保存路径
    """
    try:
        response = requests.get(url, stream=True) # 使用 stream=True 以支持下载大文件
        response.raise_for_status() # 检查请求是否成功 (状态码为 200)

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        downloaded_size = 0

        with open(save_path, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded_size += len(data)
                progress = downloaded_size / total_size_in_bytes * 100 if total_size_in_bytes else 0
                print(f"\r下载进度: {progress:.2f}%", end='') # 显示下载进度

        print("\n下载完成！")

    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")

if __name__ == '__main__':
    file_url = "https://www.example.com/example.zip" # 替换为你要下载的文件 URL
    save_path = "example.zip" # 文件保存路径
    download_file(file_url, save_path)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading # 为了防止GUI卡顿，下载操作放在线程中

class DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("简易下载器")

        # URL 输入框
        self.url_label = ttk.Label(master, text="下载链接:")
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        # 选择保存路径按钮
        self.save_path_label = ttk.Label(master, text="保存路径:")
        self.save_path_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.save_path_entry = ttk.Entry(master, width=50)
        self.save_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        self.browse_button = ttk.Button(master, text="浏览", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        # 下载按钮
        self.download_button = ttk.Button(master, text="下载", command=self.start_download)
        self.download_button.grid(row=2, column=1, pady=10)

        # 进度条
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=3, column=1, pady=5)
        self.progress_label = ttk.Label(master, text="下载进度: 0%")
        self.progress_label.grid(row=4, column=1, pady=5)

        # 下载状态信息
        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=5, column=1, pady=5)

    def browse_folder(self):
        """选择保存文件夹"""
        folder_selected = filedialog.askdirectory()
        self.save_path_entry.delete(0, tk.END) # 清空 entry
        self.save_path_entry.insert(0, folder_selected) # 填入选择的路径

    def start_download(self):
        """开始下载"""
        url = self.url_entry.get()
        save_folder = self.save_path_entry.get()

        if not url or not save_folder:
            messagebox.showerror("错误", "请填写下载链接和保存路径")
            return

        try:
            file_name = url.split('/')[-1] # 从URL中尝试获取文件名
            save_path = f"{save_folder}/{file_name}"
        except:
            messagebox.showerror("错误", "无法从URL获取文件名，请检查URL")
            return

        # 禁用下载按钮，防止重复点击
        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="准备下载...")

        # 使用线程执行下载任务，防止GUI卡顿
        threading.Thread(target=self.download_task, args=(url, save_path)).start()

    def download_task(self, url, save_path):
        """实际的下载任务（放在线程中执行）"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded_size = 0

            self.progress_bar.config(maximum=total_size_in_bytes) # 设置进度条最大值

            with open(save_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    downloaded_size += len(data)
                    self.progress_bar['value'] = downloaded_size # 更新进度条
                    progress_percent = downloaded_size / total_size_in_bytes * 100 if total_size_in_bytes else 0
                    self.progress_label.config(text=f"下载进度: {progress_percent:.2f}%") # 更新进度标签

            self.status_label.config(text="下载完成！")
            messagebox.showinfo("完成", "下载完成！文件已保存到: " + save_path)

        except requests.exceptions.RequestException as e:
            self.status_label.config(text=f"下载失败: {e}")
            messagebox.showerror("错误", f"下载失败: {e}")
        except Exception as e:
            self.status_label.config(text=f"发生错误: {e}")
            messagebox.showerror("错误", f"发生错误: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL) # 恢复下载按钮可用

if __name__ == '__main__':
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

import requests
import os

def download_file_resumable(url, save_path):
    """支持断点续传的下载函数"""
    headers = {}
    downloaded_size = 0

    if os.path.exists(save_path):
        downloaded_size = os.path.getsize(save_path) # 获取已下载的文件大小
        headers = {'Range': f'bytes={downloaded_size}-'} # 设置 Range 请求头

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        if response.status_code == 206: # 206 Partial Content 表示服务器支持断点续传
            print("支持断点续传，继续下载...")
        elif response.status_code == 200:
            print("开始全新下载...")

        total_size_in_bytes = downloaded_size + int(response.headers.get('content-length', 0)) if response.headers.get('content-length') else None
        block_size = 1024

        mode = 'ab' if downloaded_size > 0 else 'wb' # 断点续传用 'ab' (append binary)，全新下载用 'wb' (write binary)
        with open(save_path, mode) as file:
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded_size += len(data)
                if total_size_in_bytes:
                    progress = downloaded_size / total_size_in_bytes * 100
                    print(f"\r下载进度: {progress:.2f}%", end='')
                else:
                    print(f"\r已下载: {downloaded_size} bytes", end='') # 如果无法获取总大小，只显示已下载大小
        print("\n下载完成！")

    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")