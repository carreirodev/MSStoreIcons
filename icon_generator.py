"""
Microsoft Store Icon Generator
Generates all required icon variations from a single source image with maximum quality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
from PIL import Image, ImageTk
import os

# Import custom modules
from image_processor import ImageProcessor
from tooltips import bind_tooltip
from config import Config

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

        # Load configuration
        self.config = Config()

        # Set window geometry from config
        geometry = self.config.get_window_geometry()
        self.root.geometry(geometry)
        self.root.resizable(True, True)
        self.root.minsize(480, 680)  # Set minimum size to ensure all elements are visible

        # Initialize image processor
        self.image_processor = ImageProcessor()

        self.source_image_path = None
        self.source_image = None  # Keep loaded image for preview
        self.output_directory = None
        self.preview_label = None  # For image preview

        self.setup_ui()

        # Load last used settings
        self._load_last_settings()

        # Save window geometry on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

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

        # Preview frame (initially hidden)
        self.preview_frame = ttk.Frame(source_frame)
        self.preview_frame.pack(fill=tk.X, pady=5)

        source_button = ttk.Button(
            source_frame,
            text="Select Source Image",
            command=self.select_source_image
        )
        source_button.pack(fill=tk.X)

        # Icon type selection frame
        type_frame = ttk.LabelFrame(self.root, text="Icon Type", padding=8)
        type_frame.pack(fill=tk.X, padx=15, pady=5)

        # Load last icon type from config
        self.icon_type_var = tk.StringVar(value=self.config.get_last_icon_type())

        # Add callback for dynamic validation when icon type changes
        self.icon_type_var.trace_add("write", self._on_icon_type_changed)

        # Square icons radio button with tooltip
        square_radio = ttk.Radiobutton(
            type_frame,
            text="Square Icons (44x44, 150x150, 50x50) - 20 variations",
            variable=self.icon_type_var,
            value="square"
        )
        square_radio.pack(anchor=tk.W, pady=2)
        bind_tooltip(square_radio, tooltip_key="square")

        # Wide icons radio button with tooltip
        wide_radio = ttk.Radiobutton(
            type_frame,
            text="Wide Icons (310x150) - 5 variations",
            variable=self.icon_type_var,
            value="wide"
        )
        wide_radio.pack(anchor=tk.W, pady=2)
        bind_tooltip(wide_radio, tooltip_key="wide")

        # ICO multisize radio button with tooltip
        ico_radio = ttk.Radiobutton(
            type_frame,
            text="ICO Multisize (16-512px) - 1 .ico file with 7 sizes",
            variable=self.icon_type_var,
            value="ico"
        )
        ico_radio.pack(anchor=tk.W, pady=2)
        bind_tooltip(ico_radio, tooltip_key="ico")

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

    def _load_last_settings(self):
        """Load last used directories from config."""
        # Note: We don't auto-select files, just remember directories
        # Icon type is already loaded in setup_ui
        pass

    def _on_closing(self):
        """Save window geometry before closing."""
        self.config.set_window_geometry(self.root.geometry())
        self.root.destroy()

    def _on_icon_type_changed(self, *args):
        """Called when icon type selection changes - revalidate aspect ratio."""
        if self.source_image_path and self.source_image:
            self._validate_and_update_source_label()

    def _validate_and_update_source_label(self):
        """Validate aspect ratio and update source label with warning if needed."""
        if not self.source_image:
            return

        width, height = self.source_image.size
        icon_type = self.icon_type_var.get()

        # Check aspect ratio based on selected icon type
        is_valid = True
        warning_icon = ""

        if icon_type in ["square", "ico"]:
            aspect_ratio = width / height if height > 0 else 0
            if abs(aspect_ratio - 1.0) > 0.05:  # 5% tolerance
                is_valid = False
                warning_icon = " ⚠️"

        elif icon_type == "wide":
            aspect_ratio = width / height if height > 0 else 0
            expected_ratio = 310 / 150
            if abs(aspect_ratio - expected_ratio) > 0.1:  # 10% tolerance
                is_valid = False
                warning_icon = " ⚠️"

        # Update label
        file_name = Path(self.source_image_path).name
        size_info = f" ({width}x{height})"

        if is_valid:
            self.source_label.config(
                text=f"✓ {file_name}{size_info}",
                foreground="green"
            )
        else:
            self.source_label.config(
                text=f"{warning_icon} {file_name}{size_info} - Aspect ratio não recomendado",
                foreground="orange"
            )

    def _create_preview(self, img_path: str):
        """Create and display a thumbnail preview of the selected image."""
        try:
            # Clear existing preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()

            # Load and resize image for preview
            img = Image.open(img_path)

            # Calculate thumbnail size maintaining aspect ratio
            preview_size = 100
            img.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Create label with image
            preview_label = ttk.Label(self.preview_frame, image=photo)
            preview_label.image = photo  # Keep reference to prevent garbage collection
            preview_label.pack()

        except Exception as e:
            print(f"Could not create preview: {e}")

    def select_source_image(self):
        """Select the source image file"""
        # Use last directory from config if available
        initial_dir = self.config.get_last_source_directory()

        file_path = filedialog.askopenfilename(
            title="Select Source Image",
            initialdir=initial_dir if initial_dir else None,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                # Save directory for next time
                self.config.set_last_source_directory(str(Path(file_path).parent))

                # Load image using ImageProcessor
                self.source_image = self.image_processor.load_image(file_path)
                self.source_image_path = file_path

                # Create preview
                self._create_preview(file_path)

                # Validate and update label
                self._validate_and_update_source_label()

                # Check aspect ratio and show error if needed
                width, height = self.source_image.size
                icon_type = self.icon_type_var.get()

                if icon_type in ["square", "ico"]:
                    aspect_ratio = width / height if height > 0 else 0
                    if abs(aspect_ratio - 1.0) > 0.05:
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
                    aspect_ratio = width / height if height > 0 else 0
                    expected_ratio = 310 / 150
                    if abs(aspect_ratio - expected_ratio) > 0.1:
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

            except Exception as e:
                messagebox.showerror("Error", f"Could not read image:\n{str(e)}")

    def select_output_directory(self):
        """Select the output directory"""
        # Use last directory from config if available
        initial_dir = self.config.get_last_output_directory()

        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir if initial_dir else None
        )

        if dir_path:
            self.output_directory = dir_path
            self.config.set_last_output_directory(dir_path)

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

        # Save last icon type selection
        self.config.set_last_icon_type(self.icon_type_var.get())

        self.generate_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.generate_icons)
        thread.start()

    def generate_icons(self):
        """Generate all required icon variations"""
        try:
            self.update_status("Opening source image...")

            # Use already loaded image
            source_img = self.source_image

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

                # Use ImageProcessor for high-quality generation
                output_path = Path(self.output_directory) / filename
                self.image_processor.generate_png_icon(
                    source_img,
                    (width, height),
                    output_path
                )

                self.progress_bar["value"] = idx + 1
                self.root.update()

            self.update_status(f"✓ Successfully generated {len(configs)} icon variations!", "green")

            # Show success dialog with "Open Folder" button
            self._show_success_dialog(
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
            self.progress_bar["maximum"] = len(ICO_SIZES) + 1
            self.progress_bar["value"] = 0

            self.update_status("Generating ICO multisize layers...")

            # Use ImageProcessor to generate ICO
            output_path = Path(self.output_directory) / "icon.ico"
            self.image_processor.generate_ico_from_source(
                source_img,
                ICO_SIZES,
                output_path
            )

            size_list = ", ".join([f"{s}px" for s in ICO_SIZES])
            self.progress_bar["value"] = len(ICO_SIZES) + 1
            self.update_status(f"✓ Successfully generated icon.ico with {len(ICO_SIZES)} sizes!", "green")

            # Show success dialog with "Open Folder" button
            self._show_success_dialog(
                f"Successfully generated icon.ico!\n\n"
                f"Sizes included: {size_list}\n\n"
                f"Output directory:\n{self.output_directory}"
            )

        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}", "red")
            messagebox.showerror("Error", f"Failed to generate ICO file:\n{str(e)}")
            raise

    def _show_success_dialog(self, message: str):
        """Show success dialog with 'Open Folder' button."""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Success")
        dialog.geometry("400x220")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog on parent window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Success icon and message
        ttk.Label(
            dialog,
            text="✓",
            font=("Arial", 32),
            foreground="green"
        ).pack(pady=10)

        ttk.Label(
            dialog,
            text=message,
            justify=tk.LEFT,
            wraplength=360
        ).pack(pady=10, padx=20)

        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)

        # Open Folder button
        def open_folder():
            try:
                os.startfile(self.output_directory)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")

        ttk.Button(
            button_frame,
            text="📂 Open Folder",
            command=open_folder,
            width=18
        ).pack(side=tk.LEFT, padx=5)

        # OK button
        ttk.Button(
            button_frame,
            text="OK",
            command=dialog.destroy,
            width=18
        ).pack(side=tk.LEFT, padx=5)

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
