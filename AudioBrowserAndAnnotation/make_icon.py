#!/usr/bin/env python3
# make_icon.py  — create app_icon.png and app_icon.ico using PyQt6 (no extra deps)

import sys
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QApplication

def draw_pix(size=256):
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    # Folder
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#FFCB2B"))
    p.drawRoundedRect(int(size*0.11), int(size*0.33), int(size*0.78), int(size*0.50), int(size*0.08), int(size*0.08))
    p.drawRoundedRect(int(size*0.22), int(size*0.25), int(size*0.35), int(size*0.14), int(size*0.06), int(size*0.06))
    # Note
    p.setBrush(QColor("#222")); p.setPen(QColor("#222"))
    p.drawRect(int(size*0.59), int(size*0.31), int(size*0.045), int(size*0.36))
    p.drawEllipse(int(size*0.46), int(size*0.58), int(size*0.15), int(size*0.11))
    # Play triangle
    p.setBrush(QColor("#2E7D32")); p.setPen(Qt.PenStyle.NoPen)
    pts = [QPoint(int(size*0.27), int(size*0.47)), QPoint(int(size*0.27), int(size*0.70)), QPoint(int(size*0.47), int(size*0.585))]
    p.drawPolygon(*pts)
    p.end()
    return pm

def main():
    app = QApplication(sys.argv)
    pm = draw_pix(256)
    pm.save("app_icon.png", "PNG")
    icon = QIcon(pm)
    # Save as .ico (Qt supports ICO)
    icon_pix = QPixmap(pm)
    icon_pix.save("app_icon.ico", "ICO")
    print("Wrote app_icon.png and app_icon.ico")

if __name__ == "__main__":
    main()
