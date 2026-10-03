#!/usr/bin/env python3
import os
import time
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

APP_ID = "ram_zram_swap_indicator_hd"

class RamIndicator:
    def __init__(self):
        initial_icon = self.create_icon_image("0", 0)
        
        self.indicator = appindicator.Indicator.new(
            APP_ID,
            initial_icon,
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_icon_full(initial_icon, "RAM Usage")
        
        self.menu = Gtk.Menu()
        
        self.ram_item = Gtk.MenuItem(label="RAM: ...")
        self.zram_item = Gtk.MenuItem(label="ZRAM: ...")
        self.swap_item = Gtk.MenuItem(label="SWAP (Dysk): ...")
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
        
        self.last_icon_path = initial_icon
        
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

    def create_icon_image(self, percent_text, ram_pct):
        img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if ram_pct <= 75:
            color = "#4caf50"
        elif ram_pct <= 89:
            color = "#ffeb3b"
        else:
            color = "#f44336"
            
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, 56)
                    break
                except Exception:
                    pass
                    
        if font is None:
            font = ImageFont.load_default()
            
        try:
            bbox = draw.textbbox((0, 0), percent_text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (96 - w) / 2
            y = (96 - h) / 2 - 8
        except AttributeError:
            x = 20
            y = 20
            
        draw.text((x, y), percent_text, fill=color, font=font)
        
        if hasattr(self, 'last_icon_path') and self.last_icon_path and os.path.exists(self.last_icon_path):
            try:
                os.remove(self.last_icon_path)
            except Exception:
                pass
                
        icon_path = f"/tmp/ram_hd_{int(time.time() * 1000)}.png"
        img.save(icon_path)
        return icon_path

    def update_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        zram_used, zram_total, zram_pct = self.get_zram_usage()
        
        ram_pct = int(mem.percent)
        
        swap_used = max(0, swap.used - zram_used)
        swap_total = max(0, swap.total - zram_total)
        swap_pct = int((swap_used / swap_total * 100) if swap_total > 0 else 0)
        
        self.ram_item.set_label(f"RAM: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB ({ram_pct}%)")
        self.zram_item.set_label(f"ZRAM: {zram_used // (1024**2)} MB / {zram_total // (1024**2)} MB ({int(zram_pct)}%)")
        self.swap_item.set_label(f"SWAP (Dysk): {swap_used // (1024**2)} MB / {swap_total // (1024**2)} MB ({swap_pct}%)")
        
        icon_path = self.create_icon_image(str(ram_pct), ram_pct)
        self.indicator.set_icon_full(icon_path, "RAM Usage")
        self.last_icon_path = icon_path
        
        return True

    def clear_memory(self, widget):
        os.system("pkexec sh -c 'sync && echo 3 > /proc/sys/vm/drop_caches'")

    def quit(self, widget):
        Gtk.main_quit()

if __name__ == "__main__":
    indicator = RamIndicator()
    Gtk.main()
