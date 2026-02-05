import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import os
import threading
import shutil
import json
import tempfile
import time


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_window = ttk.Frame(self.canvas)
        self.scrollable_window.bind("<Configure>",
                                    lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_window, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class RealESRGAN_Strict_GUI:
    def __init__(self, master):
        self.master = master
        master.title("RealESRGAN Pro - STRICT SYNC MODE")
        master.geometry("750x850")

        self.mode = tk.StringVar(value="Image")
        self.realesrgan_path = tk.StringVar()
        self.model_var = tk.StringVar(value="realesr-animevideov3")
        self.match_source_fps = tk.BooleanVar(value=True)
        self.is_running = False
        self.stop_requested = False
        self.current_subprocess = None

        main_wrapper = ScrollableFrame(master)
        main_wrapper.pack(fill="both", expand=True)
        self.body = main_wrapper.scrollable_window

        # 1. Config
        config_frame = ttk.LabelFrame(self.body, text="Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(config_frame, text="RealESRGAN Exe:").grid(row=0, column=0, sticky="e")
        tk.Entry(config_frame, textvariable=self.realesrgan_path, width=50).grid(row=0, column=1, padx=5)
        tk.Button(config_frame, text="Browse Exe", command=self.browse_exe).grid(row=0, column=2)

        # 2. Mode
        mode_frame = tk.Frame(self.body)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Image", variable=self.mode, value="Image", command=self.update_mode).pack(
            side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Video", variable=self.mode, value="Video", command=self.update_mode).pack(
            side=tk.LEFT, padx=10)

        # 3. Settings
        self.content_frame = ttk.LabelFrame(self.body, text="Job Settings", padding=10)
        self.content_frame.pack(fill="x", padx=10, pady=5)
        self.create_widgets()
        self.update_mode()

        # 4. Logs
        log_frame = ttk.LabelFrame(self.body, text="Progress & Logs", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.progress_label = tk.Label(log_frame, text="Ready")
        self.progress_label.pack(anchor="w")
        self.progress_bar = ttk.Progressbar(log_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)

        self.run_btn = tk.Button(self.body, text="START PROCESS", command=self.toggle_process, bg="#dddddd", height=2,
                                 font=("Arial", 10, "bold"))
        self.run_btn.pack(fill="x", padx=10, pady=20)

    def create_widgets(self):
        self.lbl_input = tk.Label(self.content_frame, text="Input File:")
        self.entry_input = tk.Entry(self.content_frame, width=50)
        self.btn_browse_input = tk.Button(self.content_frame, text="Browse", command=self.browse_input)
        self.lbl_model = tk.Label(self.content_frame, text="Model:")
        self.combo_model = ttk.Combobox(self.content_frame, textvariable=self.model_var, state="readonly",
                                        values=["realesr-animevideov3", "realesrgan-x4plus", "realesrgan-x4plus-anime"])
        self.lbl_scale = tk.Label(self.content_frame, text="Scale (-s):")
        self.entry_scale = tk.Entry(self.content_frame, width=10)
        self.entry_scale.insert(0, "4")
        self.lbl_format = tk.Label(self.content_frame, text="Format (-f):")
        self.entry_format = tk.Entry(self.content_frame, width=10)
        self.entry_format.insert(0, "jpg")
        self.chk_fps = tk.Checkbutton(self.content_frame, text="Match Source FPS", variable=self.match_source_fps,
                                      command=self.toggle_fps)
        self.lbl_fps_manual = tk.Label(self.content_frame, text="Manual FPS:")
        self.entry_fps = tk.Entry(self.content_frame, width=10)
        self.entry_fps.insert(0, "30")

    def update_mode(self):
        for widget in self.content_frame.winfo_children(): widget.grid_forget()
        self.lbl_input.grid(row=0, column=0, sticky="e", pady=5)
        self.entry_input.grid(row=0, column=1, padx=5, pady=5)
        self.btn_browse_input.grid(row=0, column=2, pady=5)
        self.lbl_model.grid(row=1, column=0, sticky="e", pady=5)
        self.combo_model.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.lbl_scale.grid(row=2, column=0, sticky="e", pady=5)
        self.entry_scale.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.lbl_format.grid(row=3, column=0, sticky="e", pady=5)
        self.entry_format.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        if self.mode.get() == "Video":
            self.chk_fps.grid(row=4, column=1, sticky="w", padx=5, pady=5)
            self.lbl_fps_manual.grid(row=5, column=0, sticky="e", pady=5)
            self.entry_fps.grid(row=5, column=1, sticky="w", padx=5, pady=5)
            self.toggle_fps()
            if self.entry_format.get() == "png": self.entry_format.delete(0, tk.END); self.entry_format.insert(0, "jpg")
        else:
            if self.entry_format.get() == "jpg": self.entry_format.delete(0, tk.END); self.entry_format.insert(0, "png")

    def toggle_fps(self):
        if self.match_source_fps.get():
            self.entry_fps.config(state="disabled")
        else:
            self.entry_fps.config(state="normal")

    def browse_exe(self):
        f = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")])
        if f: self.realesrgan_path.set(f)

    def browse_input(self):
        ftypes = [("Images", "*.jpg *.png")] if self.mode.get() == "Image" else [("Videos", "*.mp4 *.mkv *.avi")]
        f = filedialog.askopenfilename(filetypes=ftypes)
        if f: self.entry_input.delete(0, tk.END); self.entry_input.insert(0, f)

    def log(self, msg):
        self.master.after(0, lambda: self._log_safe(msg))

    def _log_safe(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def update_progress(self, val, text):
        self.progress_bar['value'] = val
        self.progress_label.config(text=text)

    def toggle_process(self):
        if self.is_running:
            self.stop_requested = True
            self.run_btn.config(text="STOPPING...", bg="#ffdddd", state="disabled")
            if self.current_subprocess:
                try:
                    self.current_subprocess.terminate()
                except:
                    pass
        else:
            if not self.realesrgan_path.get() or not self.entry_input.get():
                messagebox.showerror("Error", "Please select Executable and Input file.")
                return
            self.stop_requested = False
            self.is_running = True
            self.run_btn.config(text="STOP PROCESS", bg="#ffaaaa")
            self.log_text.config(state="normal");
            self.log_text.delete(1.0, tk.END);
            self.log_text.config(state="disabled")
            self.progress_bar['value'] = 0
            threading.Thread(target=self.process_job, daemon=True).start()

    def run_subprocess_live(self, command):
        if self.stop_requested: return
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.current_subprocess = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
            startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        while True:
            if self.stop_requested:
                self.current_subprocess.terminate();
                break
            line = self.current_subprocess.stdout.readline()
            if not line and self.current_subprocess.poll() is not None: break
            if line: self.log(line.strip())
        self.current_subprocess.wait()
        self.current_subprocess = None

    def get_fps_data(self, path):
        """ Returns the FPS as a float. Defaults to 30.0 if failed. """
        try:
            cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of",
                   "json", path]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            data = json.loads(result.stdout)
            fps_str = data['streams'][0].get('r_frame_rate', "30/1")
            num, den = map(int, fps_str.split('/'))
            return num / den if den != 0 else 30.0
        except:
            return 30.0

    def process_job(self):
        try:
            exe_path = self.realesrgan_path.get()
            input_file = self.entry_input.get()
            model = self.model_var.get()
            scale = self.entry_scale.get()
            fmt = self.entry_format.get()
            input_dir = os.path.dirname(input_file)

            if self.mode.get() == "Image":
                self.log("--- Image Mode ---")
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(input_dir, f"{base_name}_upscaled.{fmt}")
                cmd = [exe_path, "-i", input_file, "-o", output_file, "-n", model, "-s", scale, "-f", fmt]
                self.run_subprocess_live(cmd)
                if os.path.exists(output_file):
                    self.log(f"SUCCESS: Saved to {output_file}")
                    messagebox.showinfo("Done", f"File saved:\n{output_file}")
            else:
                self.log("--- Video Mode (Strict Sync) ---")

                # 1. Setup Temp
                with tempfile.TemporaryDirectory() as job_dir:
                    frames_src = os.path.join(job_dir, "src")
                    frames_dst = os.path.join(job_dir, "dst")
                    os.makedirs(frames_src);
                    os.makedirs(frames_dst)

                    # 2. Determine Exact FPS
                    if self.match_source_fps.get():
                        target_fps = self.get_fps_data(input_file)
                        self.log(f"Detected Source FPS: {target_fps}")
                    else:
                        target_fps = float(self.entry_fps.get())
                        self.log(f"Manual Target FPS: {target_fps}")

                    # 3. EXTRACT ALL FRAMES (Wait for finish)
                    self.log("Step 1/3: Extracting Frames... (Please Wait)")
                    extract_cmd = [
                        "ffmpeg", "-i", input_file,
                        "-vsync", "cfr",  # Force Constant Frame Rate
                        "-r", str(target_fps),  # Force exact FPS
                        "-qscale:v", "1",
                        os.path.join(frames_src, f"frame%08d.{fmt}")
                    ]
                    self.run_subprocess_live(extract_cmd)
                    if self.stop_requested: return

                    # 4. COUNT FRAMES (The only way to be 100% accurate)
                    self.log("Counting extracted frames...")
                    actual_frames = len(os.listdir(frames_src))
                    if actual_frames == 0:
                        raise Exception("Extraction failed. No frames found.")
                    self.log(f"Exact Frame Count: {actual_frames}")

                    # 5. ENHANCE
                    self.log(f"Step 2/3: Upscaling {actual_frames} Frames...")
                    enhance_cmd = [exe_path, "-i", frames_src, "-o", frames_dst, "-n", model, "-s", scale, "-f", fmt]

                    startupinfo = None
                    if os.name == 'nt':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    self.current_subprocess = subprocess.Popen(
                        enhance_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                        startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )

                    while True:
                        if self.stop_requested: self.current_subprocess.terminate(); break
                        line = self.current_subprocess.stdout.readline()
                        if not line and self.current_subprocess.poll() is not None: break
                        if line:
                            l = line.strip()
                            if "0.00%" not in l: self.log(l)

                            # Update UI based on ACTUAL output files
                            try:
                                done_count = len(os.listdir(frames_dst))
                                prog = (done_count / actual_frames) * 100
                                # Clamp to 100% max
                                prog = min(100.0, prog)
                                self.master.after(0, lambda p=prog, c=done_count: self.update_progress(p,
                                                                                                       f"Upscaling: {c}/{actual_frames} ({int(p)}%)"))
                            except:
                                pass

                    self.current_subprocess = None
                    if self.stop_requested: return

                    # 6. MERGE (Using the EXACT same FPS as extraction)
                    self.log("Step 3/3: Merging Video...")
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    safe_output_path = os.path.join(input_dir, f"{base_name}_UNSAVED_RESULT.mp4")
                    if os.path.exists(safe_output_path): os.remove(safe_output_path)

                    merge_cmd = [
                        "ffmpeg", "-r", str(target_fps),  # STRICT SYNC
                        "-i", os.path.join(frames_dst, f"frame%08d.{fmt}"),
                        "-i", input_file,
                        "-map", "0:v:0", "-map", "1:a?",
                        "-c:a", "copy", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        safe_output_path
                    ]
                    self.run_subprocess_live(merge_cmd)

                    if os.path.exists(safe_output_path):
                        self.log(f"SAVED: {safe_output_path}")
                        self.master.after(0, lambda: self._prompt_rename(safe_output_path))
                    else:
                        self.log("CRITICAL: Merge failed.")

        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_running = False
            self.stop_requested = False
            self.master.after(0, lambda: self.run_btn.config(text="START PROCESS", bg="#dddddd", state="normal"))

    def _prompt_rename(self, safe_file):
        self.update_progress(100, "Done!")
        resp = messagebox.askyesno("Finished",
                                   f"File saved securely at:\n{safe_file}\n\nDo you want to rename/move it?")
        if resp:
            out_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video", "*.mp4")])
            if out_path:
                try:
                    if os.path.exists(out_path): os.remove(out_path)
                    shutil.move(safe_file, out_path)
                    messagebox.showinfo("Success", f"Moved to:\n{out_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not move.\nFile is still at: {safe_file}\n{e}")
        else:
            messagebox.showinfo("File Safe", f"File is located at:\n{safe_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RealESRGAN_Strict_GUI(root)
    root.mainloop()
