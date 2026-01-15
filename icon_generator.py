"""
Microsoft Store Icon Generator
Generates all required icon variations from a single source image with maximum quality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
from PIL import Image
import os

# Define all required Microsoft Store icon sizes and names
SQUARE_CONFIGS = [
    # Square44x44Logo variations
    ("Square44x44Logo.scale-100.png", 44, 44),
    ("Square44x44Logo.scale-125.png", 55, 55),
    ("Square44x44Logo.scale-150.png", 66, 66),
    ("Square44x44Logo.scale-200.png", 88, 88),
    ("Square44x44Logo.scale-400.png", 176, 176),
    ("Square44x44Logo.targetsize-16_altform-unplated.png", 16, 16),
    ("Square44x44Logo.targetsize-24_altform-unplated.png", 24, 24),
    ("Square44x44Logo.targetsize-32_altform-unplated.png", 32, 32),
    ("Square44x44Logo.targetsize-48_altform-unplated.png", 48, 48),
    ("Square44x44Logo.targetsize-256_altform-unplated.png", 256, 256),
    
    # Square150x150Logo variations
    ("Square150x150Logo.scale-100.png", 150, 150),
    ("Square150x150Logo.scale-125.png", 188, 188),
    ("Square150x150Logo.scale-150.png", 225, 225),
    ("Square150x150Logo.scale-200.png", 300, 300),
    ("Square150x150Logo.scale-400.png", 600, 600),
    
    # StoreLogo variations (base size 50x50)
    ("StoreLogo.scale-100.png", 50, 50),
    ("StoreLogo.scale-125.png", 63, 63),
    ("StoreLogo.scale-150.png", 75, 75),
    ("StoreLogo.scale-200.png", 100, 100),
    ("StoreLogo.scale-400.png", 200, 200),
]

WIDE_CONFIGS = [
    # Wide310x150Logo variations (base size 310x150)
    ("Wide310x150Logo.scale-100.png", 310, 150),
    ("Wide310x150Logo.scale-125.png", 388, 188),
    ("Wide310x150Logo.scale-150.png", 465, 225),
    ("Wide310x150Logo.scale-200.png", 620, 300),
    ("Wide310x150Logo.scale-400.png", 1240, 600),
]

# ICO multisize configurations
ICO_SIZES = [16, 32, 48, 64, 128, 256, 512]

ICON_CONFIGS = {
    "square": SQUARE_CONFIGS,
    "wide": WIDE_CONFIGS,
    "ico": [],  # ICO multisize doesn't use the same config structure
}


class IconGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Microsoft Store Icon Generator")
        self.root.geometry("480x550")
        self.root.resizable(False, False)
        
        self.source_image_path = None
        self.output_directory = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = ttk.Label(
            self.root,
            text="Microsoft Store Icon Generator",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=8)
        
        # Description
        desc_label = ttk.Label(
            self.root,
            text="Select image and output directory to generate all icons",
            justify=tk.CENTER
        )
        desc_label.pack(pady=3)
        
        # Source image frame
        source_frame = ttk.LabelFrame(self.root, text="Source Image", padding=8)
        source_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.source_label = ttk.Label(source_frame, text="No image selected", foreground="gray")
        self.source_label.pack(fill=tk.X, pady=2)
        
        source_button = ttk.Button(
            source_frame,
            text="Select Source Image",
            command=self.select_source_image
        )
        source_button.pack(fill=tk.X)
        
        # Icon type selection frame
        type_frame = ttk.LabelFrame(self.root, text="Icon Type", padding=8)
        type_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.icon_type_var = tk.StringVar(value="square")
        
        ttk.Radiobutton(
            type_frame,
            text="Square Icons (44x44, 150x150, 50x50) - 20 variations",
            variable=self.icon_type_var,
            value="square"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            type_frame,
            text="Wide Icons (310x150) - 5 variations",
            variable=self.icon_type_var,
            value="wide"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            type_frame,
            text="ICO Multisize (16-512px) - 1 .ico file with 7 sizes",
            variable=self.icon_type_var,
            value="ico"
        ).pack(anchor=tk.W, pady=2)
        
        # Info about aspect ratio
        info_frame = ttk.Frame(type_frame)
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            info_frame,
            text="ℹ Square/ICO: use 1:1 image  |  Wide: use 310x150 image",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W)
        
        # Output directory frame
        output_frame = ttk.LabelFrame(self.root, text="Output Directory", padding=8)
        output_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.output_label = ttk.Label(output_frame, text="No directory selected", foreground="gray")
        self.output_label.pack(fill=tk.X, pady=2)
        
        output_button = ttk.Button(
            output_frame,
            text="Select Output Directory",
            command=self.select_output_directory
        )
        output_button.pack(fill=tk.X)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=8)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=3)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", foreground="blue")
        self.status_label.pack(fill=tk.X, pady=2)
        
        # Generate button - styled with better appearance
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=15, pady=8)
        
        self.generate_button = ttk.Button(
            button_frame,
            text="▶ Generate Icons",
            command=self.generate_icons_threaded,
            style="Accent.TButton",
            width=30
        )
        self.generate_button.pack()
    
    def select_source_image(self):
        """Select the source image file"""
        file_path = filedialog.askopenfilename(
            title="Select Source Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Check image dimensions
                img = Image.open(file_path)
                width, height = img.size
                
                icon_type = self.icon_type_var.get()
                
                # Check aspect ratio based on selected icon type
                if icon_type in ["square", "ico"]:
                    # For square icons and ICO, aspect ratio should be 1:1
                    aspect_ratio = width / height if height > 0 else 0
                    
                    if abs(aspect_ratio - 1.0) > 0.05:  # Allow 5% tolerance
                        icon_name = "Square" if icon_type == "square" else "ICO"
                        messagebox.showerror(
                            "Invalid Aspect Ratio",
                            f"Current image size: {width}x{height}\n"
                            f"Aspect ratio: {aspect_ratio:.2f}\n\n"
                            f"{icon_name} icons require a 1:1 aspect ratio (square image)\n"
                            f"Please select a square image."
                        )
                        return
                
                elif icon_type == "wide":
                    # For wide icons, aspect ratio should be 310:150
                    aspect_ratio = width / height if height > 0 else 0
                    expected_ratio = 310 / 150  # ~2.067
                    
                    if abs(aspect_ratio - expected_ratio) > 0.1:  # Allow 10% tolerance
                        response = messagebox.askyesno(
                            "Aspect Ratio Warning",
                            f"Current image size: {width}x{height}\n"
                            f"Expected aspect ratio for Wide icons: 310x150\n\n"
                            f"Your image aspect ratio: {aspect_ratio:.2f}\n"
                            f"Expected aspect ratio: {expected_ratio:.2f}\n\n"
                            f"Wide icons may not look correct.\n"
                            f"Continue anyway?"
                        )
                        if not response:
                            return
                
                self.source_image_path = file_path
                file_name = Path(file_path).name
                size_info = f" ({width}x{height})"
                self.source_label.config(
                    text=f"✓ {file_name}{size_info}",
                    foreground="green"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image:\n{str(e)}")
    
    def select_output_directory(self):
        """Select the output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        
        if dir_path:
            self.output_directory = dir_path
            dir_name = Path(dir_path).name or dir_path
            self.output_label.config(text=f"✓ {dir_name}", foreground="green")
    
    def generate_icons_threaded(self):
        """Generate icons in a separate thread to avoid freezing the UI"""
        if not self.source_image_path:
            messagebox.showerror("Error", "Please select a source image")
            return
        
        if not self.output_directory:
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        self.generate_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.generate_icons)
        thread.start()
    
    def generate_icons(self):
        """Generate all required icon variations"""
        try:
            # Open the source image
            self.update_status("Opening source image...")
            source_img = Image.open(self.source_image_path)
            
            # Convert to RGBA if necessary (preserve transparency)
            if source_img.mode != "RGBA":
                source_img = source_img.convert("RGBA")
            
            icon_type = self.icon_type_var.get()
            
            # Handle ICO multisize generation separately
            if icon_type == "ico":
                self.generate_ico_multisize(source_img)
                return
            
            configs = ICON_CONFIGS[icon_type]
            
            self.progress_bar["maximum"] = len(configs)
            self.progress_bar["value"] = 0
            
            # Generate each icon variation
            for idx, (filename, width, height) in enumerate(configs):
                self.update_status(f"Generating {filename}...")
                
                # Resize with maximum quality
                # Use LANCZOS resampling for best quality
                resized_img = source_img.resize(
                    (width, height),
                    Image.Resampling.LANCZOS
                )
                
                # Save with maximum quality
                output_path = Path(self.output_directory) / filename
                resized_img.save(
                    output_path,
                    "PNG",
                    optimize=False  # Don't optimize to preserve quality
                )
                
                self.progress_bar["value"] = idx + 1
                self.root.update()
            
            self.update_status(f"✓ Successfully generated {len(configs)} icon variations!", "green")
            messagebox.showinfo(
                "Success",
                f"Successfully generated {len(configs)} icon variations!\n\n"
                f"Type: {icon_type.capitalize()}\n"
                f"Output directory:\n{self.output_directory}"
            )
            
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}", "red")
            messagebox.showerror("Error", f"Failed to generate icons:\n{str(e)}")
        
        finally:
            self.generate_button.config(state=tk.NORMAL)
    
    def generate_ico_multisize(self, source_img):
        """Generate a multisize .ico file with maximum quality"""
        try:
            self.progress_bar["maximum"] = len(ICO_SIZES)
            self.progress_bar["value"] = 0
            
            # Create resized versions for all sizes
            icon_images = []
            for idx, size in enumerate(ICO_SIZES):
                self.update_status(f"Preparing {size}x{size} icon layer...")
                
                # Resize with maximum quality using LANCZOS resampling
                resized_img = source_img.resize(
                    (size, size),
                    Image.Resampling.LANCZOS
                )
                
                icon_images.append(resized_img)
                self.progress_bar["value"] = idx + 1
                self.root.update()
            
            # Save as multisize ICO file
            self.update_status("Saving icon.ico file...")
            output_path = Path(self.output_directory) / "icon.ico"
            
            # Save the first image and append the rest as additional sizes
            # PIL automatically handles ICO format with multiple sizes
            icon_images[0].save(
                output_path,
                format="ICO",
                sizes=[(size, size) for size in ICO_SIZES],
                append_images=icon_images[1:]
            )
            
            size_list = ", ".join([f"{s}px" for s in ICO_SIZES])
            self.update_status(f"✓ Successfully generated icon.ico with {len(ICO_SIZES)} sizes!", "green")
            messagebox.showinfo(
                "Success",
                f"Successfully generated icon.ico!\n\n"
                f"Sizes included: {size_list}\n\n"
                f"Output directory:\n{self.output_directory}"
            )
            
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}", "red")
            messagebox.showerror("Error", f"Failed to generate ICO file:\n{str(e)}")
            raise
    
    def update_status(self, message, color="blue"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()


def main():
    root = tk.Tk()
    app = IconGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
