import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FFmpeg GUI")

        # メインフレームを作成
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ファイルを指定するボタンと現在指定しているファイル名を表示するラベル
        self.file_label = ttk.Label(main_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.W)
        self.file_button = ttk.Button(main_frame, text="Select File", command=self.select_file)
        self.file_button.grid(row=0, column=3, pady=5, padx=5, sticky=tk.EW)

        # 解像度を指定するラジオボタンのフレーム
        resolution_frame = ttk.LabelFrame(main_frame, text="Select Resolution", padding="10")
        resolution_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.W + tk.E)
        self.resolution_var = tk.StringVar(value="Original")
        resolutions = [("Original", "Original"), ("480p", "480p"), ("720p", "720p"), ("1080p", "1080p"), ("2K", "2K"), ("4K", "4K")]
        for idx, (text, value) in enumerate(resolutions):
            ttk.Radiobutton(resolution_frame, text=text, variable=self.resolution_var, value=value).grid(row=0, column=idx, padx=5, pady=5, sticky=tk.W)

        # 開始時刻と終了時刻を指定する入力ボックスのフレーム
        time_frame = ttk.LabelFrame(main_frame, text="Enter Start and End Time (seconds)", padding="10")
        time_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky=tk.W + tk.E)
        self.start_time_label = ttk.Label(time_frame, text="Start Time (s)")
        self.start_time_label.grid(row=0, column=0, pady=5, sticky=tk.E)
        self.start_time_entry = ttk.Entry(time_frame)
        self.start_time_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        self.end_time_label = ttk.Label(time_frame, text="End Time (s)")
        self.end_time_label.grid(row=0, column=2, pady=5, sticky=tk.E)
        self.end_time_entry = ttk.Entry(time_frame)
        self.end_time_entry.grid(row=0, column=3, pady=5, padx=5, sticky=tk.W)

        # 動画の拡張子を指定するラジオボタンのフレーム
        extension_frame = ttk.LabelFrame(main_frame, text="Select Video Extension", padding="10")
        extension_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky=tk.W + tk.E)
        self.extension_var = tk.StringVar(value="Original")
        extensions = [("Original", "Original"), ("MP4", "mp4"), ("AVI", "avi"), ("MKV", "mkv"), ("MOV", "mov"), ("WMV", "wmv")]
        for idx, (text, value) in enumerate(extensions):
            ttk.Radiobutton(extension_frame, text=text, variable=self.extension_var, value=value).grid(row=0, column=idx, padx=5, pady=5, sticky=tk.W)

        # 出力先のフォルダを指定するボタンを現在指定しているフォルダ名を表示するラベル
        self.output_folder_label = ttk.Label(main_frame, text="No folder selected")
        self.output_folder_label.grid(row=4, column=0, columnspan=3, pady=10, sticky=tk.W)
        self.output_folder_button = ttk.Button(main_frame, text="Select Folder", command=self.select_output_folder)
        self.output_folder_button.grid(row=4, column=3, pady=5, padx=5, sticky=tk.EW)

        # 決定ボタンを追加
        self.confirm_button = ttk.Button(main_frame, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=5, column=3, pady=10, padx=5, sticky=tk.EW)

        # 列の幅を指定する
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=0, minsize=150)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder_label.config(text=folder_path)

    def confirm(self):
        input_file = self.file_label.cget("text")
        output_folder = self.output_folder_label.cget("text")
        resolution = self.resolution_var.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()
        extension = self.extension_var.get()

        # 入力ファイルと出力フォルダの指定を確認
        if input_file == "No file selected" or output_folder == "No folder selected":
            messagebox.showerror("Error", "Input file and output folder must be specified")
            return

        # 入力のバリデーション
        if start_time and not start_time.isdigit():
            messagebox.showerror("Error", "Start time must be a number")
            return
        if end_time and not end_time.isdigit():
            messagebox.showerror("Error", "End time must be a number")
            return
        if start_time and end_time and int(start_time) >= int(end_time):
            messagebox.showerror("Error", "Start time must be less than end time")
            return

        # 出力ファイルの拡張子を決定
        if extension == "Original":
            output_extension = os.path.splitext(input_file)[1]
        else:
            output_extension = f".{extension}"

        # 元ファイル名を取得して出力ファイルの名前を作成
        input_filename = os.path.splitext(os.path.basename(input_file))[0]
        output_filename = f"{input_filename}_modified{output_extension}"

        # 出力ファイルのパスを作成
        output_file = os.path.join(output_folder, output_filename)

        # ffmpegコマンドを作成
        cmd = ["ffmpeg", "-i", input_file]

        # 解像度の指定
        if resolution != "Original":
            resolution_map = {"480p": "640x480", "720p": "1280x720", "1080p": "1920x1080", "2K": "2048x1080", "4K": "3840x2160"}
            cmd.extend(["-s", resolution_map[resolution]])

        # トリミングの指定
        if start_time:
            cmd.extend(["-ss", start_time])
        if end_time:
            cmd.extend(["-to", end_time])

        # 出力ファイルの指定
        cmd.append(output_file)

        # ffmpegコマンドの実行
        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Success", f"Video processed successfully and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to process video: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
