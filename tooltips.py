"""
Custom tooltip system for Tkinter widgets.
Provides helpful explanations for icon types and UI elements.
"""

import tkinter as tk
from typing import Optional


class CustomTooltip:
    """
    Custom tooltip that appears on hover over a widget.
    Shows helpful text after a brief delay.
    """

    def __init__(self, widget: tk.Widget, text: str, delay: int = 800):
        """
        Initialize tooltip for a widget.

        Args:
            widget: The Tkinter widget to attach tooltip to
            text: The tooltip text to display
            delay: Delay in milliseconds before tooltip appears (default 800ms)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.schedule_id: Optional[str] = None

        # Bind mouse events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Button>", self._on_leave)  # Hide on click

    def _on_enter(self, event=None):
        """Mouse entered widget - schedule tooltip to appear."""
        self._cancel_scheduled()
        self.schedule_id = self.widget.after(self.delay, self._show_tooltip)

    def _on_leave(self, event=None):
        """Mouse left widget - hide tooltip."""
        self._cancel_scheduled()
        self._hide_tooltip()

    def _cancel_scheduled(self):
        """Cancel any scheduled tooltip appearance."""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def _show_tooltip(self):
        """Display the tooltip near the widget."""
        if self.tooltip_window or not self.text:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # No window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Create label with tooltip text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",  # Light yellow background
            foreground="#000000",  # Black text
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=6,
            wraplength=300  # Wrap long text
        )
        label.pack()

    def _hide_tooltip(self):
        """Hide the tooltip if it's showing."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# Tooltip texts for icon types
ICON_TYPE_TOOLTIPS = {
    "square": (
        "Para o ícone principal do aplicativo\n\n"
        "Usado em:\n"
        "• Microsoft Store (listagem do app)\n"
        "• Menu Iniciar (tile pequeno e médio)\n"
        "• Barra de tarefas\n"
        "• Lista de apps\n\n"
        "Gera 20 variações em diferentes escalas DPI"
    ),
    "wide": (
        "Para o tile largo do Menu Iniciar (opcional)\n\n"
        "Usado em:\n"
        "• Menu Iniciar (tile largo 310x150)\n"
        "• Tela inicial do Windows 8/8.1\n\n"
        "Aspect ratio: 310:150 (aproximadamente 2:1)\n"
        "Gera 5 variações em diferentes escalas DPI"
    ),
    "ico": (
        "Para ícones de aplicativo Windows (.exe)\n\n"
        "Usado em:\n"
        "• Arquivo executável do aplicativo\n"
        "• Atalhos na área de trabalho\n"
        "• Windows Explorer\n"
        "• Barra de título da janela\n\n"
        "Gera 1 arquivo .ico com 7 tamanhos incorporados\n"
        "(16, 32, 48, 64, 128, 256, 512 pixels)"
    )
}


def bind_tooltip(widget: tk.Widget, tooltip_key: Optional[str] = None,
                custom_text: Optional[str] = None, delay: int = 800) -> CustomTooltip:
    """
    Convenience function to bind a tooltip to a widget.

    Args:
        widget: Widget to attach tooltip to
        tooltip_key: Key from ICON_TYPE_TOOLTIPS dictionary
        custom_text: Custom tooltip text (used if tooltip_key is None)
        delay: Delay before tooltip appears in milliseconds

    Returns:
        The created CustomTooltip instance
    """
    if tooltip_key and tooltip_key in ICON_TYPE_TOOLTIPS:
        text = ICON_TYPE_TOOLTIPS[tooltip_key]
    elif custom_text:
        text = custom_text
    else:
        raise ValueError("Either tooltip_key or custom_text must be provided")

    return CustomTooltip(widget, text, delay)
