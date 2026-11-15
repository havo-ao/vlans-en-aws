#!/usr/bin/env python3
"""Recorta las capturas para el manual y oculta el número de cuenta (se corta la barra superior de la consola)."""
import pathlib
from PIL import Image, ImageDraw

R = pathlib.Path(__file__).parent.parent
OUT = R / "manual" / "img"; OUT.mkdir(exist_ok=True)
CS, MA = R / "capturas/06_cloudshell", R / "capturas/07_manual"

def guardar(im, nombre, ancho=1500):
    im = im.convert("RGB")
    if im.size[0] > ancho: im = im.resize((ancho, int(ancho * im.size[1] / im.size[0])))
    im.save(OUT / nombre, quality=88); print(nombre, im.size)

def terminal(origen, nombre, y0=72, alto=None, desde_abajo=None):
    """Recorte del terminal de CloudShell sin la barra superior, que muestra el número de cuenta."""
    im = Image.open(CS / origen); w, h = im.size
    w = int(w * .64)                                                 # el texto ocupa la parte izquierda: así se lee más grande
    if desde_abajo: caja = (0, h - 78 - desde_abajo, w, h - 78)      # 78 px: barra inferior de la consola y última línea cortada
    else: caja = (0, y0, w, y0 + (alto or 520))
    guardar(im.crop(caja), nombre)

def resaltar(im, caja, color="#FF9900", grosor=7):
    ImageDraw.Draw(im).rounded_rectangle(caja, radius=16, outline=color, width=grosor); return im

guardar(Image.open(R / "presentacion/revision/s09.jpg"), "00_arquitectura.jpg", 1500)
im = Image.open(MA / "01_pagina_capa_gratuita.png"); w, h = im.size
guardar(resaltar(im.crop((0, 0, w, int(h * .62))), (165, 628, 555, 722)), "01_capa_gratuita.png")
guardar(Image.open(R / "capturas/01_cuenta/01_correo_cuenta_lista.png"), "03_correo.png", 1100)
im = Image.open(MA / "04_menu_cuenta.png"); w, h = im.size
ImageDraw.Draw(im).rectangle((2060, 0, w, 72), fill=im.getpixel((1500, 20)))                 # oculta nombre y número de cuenta
guardar(resaltar(im.crop((0, 0, w, int(h * .56))), (1836, 4, 1908, 68)), "04_consola.png")
terminal("00_sin_terminal.png", "05_cloudshell.png", alto=300)
for origen, nombre, kw in [("p0_clonar.png", "06_clonar.png", dict(alto=420)), ("p1_preparar.png", "07_preparar.png", dict(alto=470)),
                           ("p2_desplegar.png", "08_desplegar.png", dict(desde_abajo=524)), ("p3_probar.png", "10_probar.png", dict(alto=560)),
                           ]:
    if (CS / origen).exists(): terminal(origen, nombre, **kw)
    else: print("falta", origen)
guardar(Image.open(R / "presentacion/img/demo2.png"), "09_aplicacion.png", 1200)
guardar(Image.open(R / "presentacion/img/mapa.png"), "11_mapa.png", 1500)

# El borrado: final real del destroy (46 recursos) y la verificación del guion ya corregido.
im = Image.open(CS / "p4_destruir_t16.png"); w, h = im.size
guardar(im.crop((0, 905, int(w * .64), 1252)), "12_destruir.png")
im = Image.open(CS / "p6_verificacion.png"); w, h = im.size
guardar(im.crop((0, 420, int(w * .64), 512)), "13_verificacion.png")
