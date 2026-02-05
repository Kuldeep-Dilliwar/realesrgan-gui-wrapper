import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading

class RealESRGANGUI:
    def __init__(self, master):
        self.master = master
        master.title("RealESRGAN GUI - Mommy's Helper")

        # Mode selection: Image or Video
        self.mode = tk.StringVar(value="Image")
        mode_frame = tk.Frame(master)
        mode_frame.pack(pady=10)
        tk.Label(mode_frame, text="Select Mode:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Image", variable=self.mode, value="Image", command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Video", variable=self.mode, value="Video", command=self.update_mode).pack(side=tk.LEFT, padx=5)

        self.content_frame = tk.Frame(master)
        self.content_frame.pack(pady=10)

        self.create_image_widgets()
        self.create_video_widgets()
        self.update_mode()

    def create_image_widgets(self):
        self.image_frame = tk.Frame(self.content_frame)
        # Input image selection
        tk.Label(self.image_frame, text="Input Image:").grid(row=0, column=0, sticky="e")
        self.input_image_entry = tk.Entry(self.image_frame, width=50)
        self.input_image_entry.grid(row=0, column=1, padx=5)
        tk.Button(self.image_frame, text="Browse", command=self.browse_image).grid(row=0, column=2, padx=5)

        # Output image selection
        tk.Label(self.image_frame, text="Output Image:").grid(row=1, column=0, sticky="e")
        self.output_image_entry = tk.Entry(self.image_frame, width=50)
        self.output_image_entry.grid(row=1, column=1, padx=5)
        tk.Button(self.image_frame, text="Browse", command=self.save_image).grid(row=1, column=2, padx=5)

        # Model selection
        tk.Label(self.image_frame, text="Model:").grid(row=2, column=0, sticky="e")
        self.model_var = tk.StringVar(value="realesr-animevideov3")
        self.model_menu = ttk.Combobox(self.image_frame, textvariable=self.model_var, state="readonly",
                                       values=["realesr-animevideov3", "realesrgan-x4plus", "realesrgan-x4plus-anime"])
        self.model_menu.grid(row=2, column=1, sticky="w", padx=5)

        # Scale factor
        tk.Label(self.image_frame, text="Scale Factor (-s):").grid(row=3, column=0, sticky="e")
        self.scale_entry = tk.Entry(self.image_frame, width=10)
        self.scale_entry.insert(0, "2")
        self.scale_entry.grid(row=3, column=1, sticky="w", padx=5)

        # Output format
        tk.Label(self.image_frame, text="Output Format (-f):").grid(row=4, column=0, sticky="e")
        self.format_entry = tk.Entry(self.image_frame, width=10)
        self.format_entry.insert(0, "png")
        self.format_entry.grid(row=4, column=1, sticky="w", padx=5)

        # Run button for image enhancement
        self.run_image_btn = tk.Button(self.image_frame, text="Enhance Image", command=self.run_image_enhancement)
        self.run_image_btn.grid(row=5, column=0, columnspan=3, pady=10)

    def create_video_widgets(self):
        self.video_frame = tk.Frame(self.content_frame)
        # Input video file
        tk.Label(self.video_frame, text="Input Video:").grid(row=0, column=0, sticky="e")
        self.input_video_entry = tk.Entry(self.video_frame, width=50)
        self.input_video_entry.grid(row=0, column=1, padx=5)
        tk.Button(self.video_frame, text="Browse", command=self.browse_video).grid(row=0, column=2, padx=5)

        # Output video file
        tk.Label(self.video_frame, text="Output Video:").grid(row=1, column=0, sticky="e")
        self.output_video_entry = tk.Entry(self.video_frame, width=50)
        self.output_video_entry.grid(row=1, column=1, padx=5)
        tk.Button(self.video_frame, text="Browse", command=self.save_video).grid(row=1, column=2, padx=5)

        # Model selection
        tk.Label(self.video_frame, text="Model:").grid(row=2, column=0, sticky="e")
        self.video_model_var = tk.StringVar(value="realesr-animevideov3")
        self.video_model_menu = ttk.Combobox(self.video_frame, textvariable=self.video_model_var, state="readonly",
                                             values=["realesr-animevideov3", "realesrgan-x4plus", "realesrgan-x4plus-anime"])
        self.video_model_menu.grid(row=2, column=1, sticky="w", padx=5)

        # Scale factor for video frames
        tk.Label(self.video_frame, text="Scale Factor (-s):").grid(row=3, column=0, sticky="e")
        self.video_scale_entry = tk.Entry(self.video_frame, width=10)
        self.video_scale_entry.insert(0, "2")
        self.video_scale_entry.grid(row=3, column=1, sticky="w", padx=5)

        # Frame format
        tk.Label(self.video_frame, text="Frame Format (-f):").grid(row=4, column=0, sticky="e")
        self.video_format_entry = tk.Entry(self.video_frame, width=10)
        self.video_format_entry.insert(0, "jpg")
        self.video_format_entry.grid(row=4, column=1, sticky="w", padx=5)

        # Run button for video enhancement
        self.run_video_btn = tk.Button(self.video_frame, text="Enhance Video", command=self.run_video_enhancement)
        self.run_video_btn.grid(row=5, column=0, columnspan=3, pady=10)

    def update_mode(self):
        # Show or hide widgets based on selected mode
        if self.mode.get() == "Image":
            self.video_frame.pack_forget()
            self.image_frame.pack()
        else:
            self.image_frame.pack_forget()
            self.video_frame.pack()

    def browse_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image File",
                                               filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.input_image_entry.delete(0, tk.END)
            self.input_image_entry.insert(0, file_path)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(title="Save Output Image", defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")])
        if file_path:
            self.output_image_entry.delete(0, tk.END)
            self.output_image_entry.insert(0, file_path)

    def browse_video(self):
        file_path = filedialog.askopenfilename(title="Select a Video File",
                                               filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.input_video_entry.delete(0, tk.END)
            self.input_video_entry.insert(0, file_path)

    def save_video(self):
        file_path = filedialog.asksaveasfilename(title="Save Output Video", defaultextension=".mp4",
                                                 filetypes=[("MP4", "*.mp4")])
        if file_path:
            self.output_video_entry.delete(0, tk.END)
            self.output_video_entry.insert(0, file_path)

    def run_image_enhancement(self):
        # Run image processing in a separate thread to keep the GUI responsive
        threading.Thread(target=self.process_image).start()

    def process_image(self):
        input_path = self.input_image_entry.get()
        output_path = self.output_image_entry.get()
        model = self.model_var.get()
        scale = self.scale_entry.get()
        out_format = self.format_entry.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output files, sweetie!")
            return

        # Build the command
        command = [
            "./realesrgan-ncnn-vulkan.exe",
            "-i", input_path,
            "-o", output_path,
            "-n", model,
            "-s", scale,
            "-f", out_format
        ]

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Image enhancement completed, sweetie!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def run_video_enhancement(self):
        # Run video processing in a separate thread
        threading.Thread(target=self.process_video).start()

    def process_video(self):
        input_video = self.input_video_entry.get()
        output_video = self.output_video_entry.get()
        model = self.video_model_var.get()
        scale = self.video_scale_entry.get()
        frame_format = self.video_format_entry.get()

        if not input_video or not output_video:
            messagebox.showerror("Error", "Please select both input and output video files, sweetie!")
            return

        tmp_frames = "tmp_frames"
        out_frames = "out_frames"
        os.makedirs(tmp_frames, exist_ok=True)
        os.makedirs(out_frames, exist_ok=True)

        try:
            # Step 1: Extract frames using ffmpeg
            extract_cmd = [
                "ffmpeg", "-i", input_video,
                "-qscale:v", "1", "-qmin", "1", "-qmax", "1",
                "-vsync", "0",
                os.path.join(tmp_frames, f"frame%08d.{frame_format}")
            ]
            subprocess.run(extract_cmd, check=True)

            # Step 2: Enhance frames with RealESRGAN
            process_cmd = [
                "./realesrgan-ncnn-vulkan.exe",
                "-i", tmp_frames,
                "-o", out_frames,
                "-n", model,
                "-s", scale,
                "-f", frame_format
            ]
            subprocess.run(process_cmd, check=True)

            # Step 3: Merge enhanced frames back into a video, preserving audio
            merge_cmd = [
                "ffmpeg",
                "-i", os.path.join(out_frames, f"frame%08d.{frame_format}"),
                "-i", input_video,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:a", "copy",
                "-c:v", "libx264",
                "-r", "23.98",
                "-pix_fmt", "yuv420p",
                output_video
            ]
            subprocess.run(merge_cmd, check=True)

            messagebox.showinfo("Success", "Video enhancement completed, sweetie!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during video processing: {e}")
        # Optional cleanup of temporary folders can be added here

if __name__ == "__main__":
    root = tk.Tk()
    app = RealESRGANGUI(root)
    root.mainloop()
