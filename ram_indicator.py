#!/usr/bin/env python3
import os
import psutil
from PIL import Image, ImageDraw, ImageFont
import gi

gi.require_version('Gtk', '3.0')

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as appindicator
except (ValueError, ImportError):
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as appindicator
    except (ValueError, ImportError):
        raise ImportError("Brak wymaganej biblioteki AppIndicator3 w systemie!")

from gi.repository import Gtk, GLib

APP_ID = "ram_zram_swap_indicator_clean"

class RamIndicator:
    def __init__(self):
        self.indicator = appindicator.Indicator.new(
            APP_ID,
            "utilities-system-monitor",
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        
        # Konfiguracja czcionki
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        self.font_size = 20
        
        try:
            if os.path.exists(self.font_path):
                self.font = ImageFont.truetype(self.font_path, self.font_size)
            else:
                self.font = ImageFont.load_default()
        except Exception:
            self.font = ImageFont.load_default()

        self.menu = Gtk.Menu()
        
        self.ram_item = Gtk.MenuItem(label="RAM: ...")
        self.zram_item = Gtk.MenuItem(label="ZRAM: ...")
        self.swap_item = Gtk.MenuItem(label="SWAP: ...")
        self.clean_item = Gtk.MenuItem(label="Wyczyść pamięć podręczną (Drop Caches)")
        self.quit_item = Gtk.MenuItem(label="Zamknij")
        
        self.clean_item.connect("activate", self.clear_memory)
        self.quit_item.connect("activate", self.quit)
        
        self.menu.append(self.ram_item)
        self.menu.append(self.zram_item)
        self.menu.append(self.swap_item)
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(self.clean_item)
        self.menu.append(self.quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        
        GLib.timeout_add_seconds(2, self.update_stats)

    def get_zram_usage(self):
        try:
            with open('/proc/swaps', 'r') as f:
                lines = f.readlines()
            for line in lines[1:]:
                parts = line.split()
                if 'zram' in parts[0]:
                    used = int(parts[3]) * 1024
                    total = int(parts[2]) * 1024
                    percent = (used / total) * 100 if total > 0 else 0
                    return used, total, percent
        except Exception:
            pass
        return 0, 0, 0

    def create_icon_image(self, percent_text, percent_val):
        if percent_val >= 90:
            text_color = "#ef5350"  # Czerwony
        elif percent_val >= 76:
            text_color = "#ffeb3b"  # Żółty
        else:
            text_color = "#66bb6a"  # Zielony

        img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            bbox = draw.textbbox((0, 0), percent_text, font=self.font)
            txt_width = bbox[2] - bbox[0]
            txt_height = bbox[3] - bbox[1]
            x = (24 - txt_width) / 2
            y = (24 - txt_height) / 2
        except AttributeError:
            txt_width, txt_height = draw.textsize(percent_text, font=self.font)
            x = (24 - txt_width) / 2
            y = (24 - txt_height) / 2

        shadow_color = (0, 0, 0, 128)
        offset = 1
        draw.text((x+offset, y), percent_text, font=self.font, fill=shadow_color)
        draw.text((x-offset, y), percent_text, font=self.font, fill=shadow_color)
        draw.text((x, y+offset), percent_text, font=self.font, fill=shadow_color)
        draw.text((x, y-offset), percent_text, font=self.font, fill=shadow_color)
        
        draw.text((x, y), percent_text, fill=text_color, font=self.font)
        
        icon_path = "/tmp/ram_indicator_big.png"
        img.save(icon_path)
        return icon_path

    def update_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        zram_used, zram_total, zram_pct = self.get_zram_usage()
        
        ram_pct = int(mem.percent)
        
        swap_used_exclusive = max(0, swap.used - zram_used)
        swap_total_exclusive = max(0, swap.total - zram_total)
        swap_pct_exclusive = (swap_used_exclusive / swap_total_exclusive * 100) if swap_total_exclusive > 0 else 0
        
        self.ram_item.set_label(f"RAM: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB ({ram_pct}%)")
        self.zram_item.set_label(f"ZRAM: {zram_used // (1024**2)} MB / {zram_total // (1024**2)} MB ({int(zram_pct)}%)")
        self.swap_item.set_label(f"SWAP: {swap_used_exclusive // (1024**2)} MB / {swap_total_exclusive // (1024**2)} MB ({int(swap_pct_exclusive)}%)")
        
        icon_path = self.create_icon_image(str(ram_pct), ram_pct)
        self.indicator.set_icon_full(icon_path, f"Zużycie RAM: {ram_pct}%")
        
        return True

    def clear_memory(self, widget):
        os.system("pkexec sh -c 'sync && echo 3 > /proc/sys/vm/drop_caches'")

    def quit(self, widget):
        Gtk.main_quit()

if __name__ == "__main__":
    indicator = RamIndicator()
    Gtk.main()
