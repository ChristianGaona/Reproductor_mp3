# pip install pillow
# pip install pygame

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import pygame
import os

pygame.mixer.init()

# Variables globales
lista_canciones = []
indice_actual = 0
portada_mini = None
detenido_manualmente = False
etiquetas_canciones = []

# Funciones
def reproducir():
    global detenido_manualmente
    detenido_manualmente = False
    if lista_canciones:
        try:
            pygame.mixer.music.load(lista_canciones[indice_actual])
            pygame.mixer.music.play()
            lbl_repro_titulo.config(text=os.path.basename(lista_canciones[indice_actual]))
            if portada_mini:
                lbl_repro_img.config(image=portada_mini)
                lbl_repro_img.image = portada_mini
            frame_reproduciendo.pack(after=canvas_frame, fill="x")
            resaltar_cancion_actual()
            fin_cancion()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir:\n{e}")

def resaltar_cancion_actual():
    for i, lbl in enumerate(etiquetas_canciones):
        color = "#FF2A3C" if i == indice_actual else "white"
        lbl.config(fg=color)

def fin_cancion():
    if not pygame.mixer.music.get_busy() and not detenido_manualmente:
        cambiar_cancion(1)
    elif not detenido_manualmente:
        root.after(1000, fin_cancion)

def detener():
    global detenido_manualmente
    detenido_manualmente = True
    pygame.mixer.music.stop()
    lbl_repro_titulo.config(text="")
    lbl_repro_img.config(image="")
    resaltar_cancion_actual()
    frame_reproduciendo.pack_forget()

def cambiar_cancion(direccion):
    global indice_actual
    if lista_canciones:
        indice_actual = (indice_actual + direccion) % len(lista_canciones)
        reproducir()

def biblioteca():
    global lista_canciones, indice_actual, portada_mini, etiquetas_canciones
    ruta = filedialog.askopenfilename(title="Selecciona el álbum (JSON)", filetypes=[("Archivos JSON", ".json")])
    if not ruta:
        return

    carpeta = os.path.dirname(ruta)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)

        portada_path = os.path.join(carpeta, datos["portada"])
        imagen = Image.open(portada_path).resize((150, 150))
        img = ImageTk.PhotoImage(imagen)
        lbl_portada.config(image=img)
        lbl_portada.image = img

        lbl_album.config(text=datos['album'])
        lbl_artista.config(text=datos['artista'])
        btn_reproducir.pack()
        canvas_frame.pack(pady=20, fill="x")

        mini = Image.open(portada_path).resize((30, 30))
        portada_mini = ImageTk.PhotoImage(mini)

        for widget in frame_canciones.winfo_children():
            widget.destroy()
        etiquetas_canciones.clear()

        lista_canciones = [os.path.join(carpeta, c["archivo"]) for c in datos["canciones"]]
        indice_actual = 0

        for i, cancion in enumerate(datos["canciones"], 1):
            fila = tk.Frame(frame_canciones, bg="#232324")
            fila.pack(anchor="w", pady=2, padx=10, fill="x")

            tk.Label(fila, text=f"{i}.", font=("Arial", 10), bg="#232324", fg="white", width=3).pack(side="left")
            lbl_mini = tk.Label(fila, image=portada_mini, bg="#232324")
            lbl_mini.image = portada_mini
            lbl_mini.pack(side="left", padx=(0, 5))

            lbl_nombre = tk.Label(
                fila,
                text=f"{cancion['titulo']} ({cancion['duracion']})",
                font=("Arial", 10),
                bg="#232324",
                fg="white",
                anchor="w"
            )
            lbl_nombre.pack(side="left")
            etiquetas_canciones.append(lbl_nombre)

        btn_cargar.pack_forget()
        frame_reproduciendo.pack_forget()
        frame_inferior.pack(side="bottom", fill="x", pady=25)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

# Ventana
root = tk.Tk()
root.title("Reproductor")
root.geometry("400x650")
root.configure(bg="#1c1c1e")

# Parte superior
frame_arriba = tk.Frame(root, bg="#1c1c1e")
frame_arriba.pack(fill="x")

lbl_portada = tk.Label(frame_arriba, bg="#1c1c1e")
lbl_portada.pack()

lbl_album = tk.Label(frame_arriba, font=("Arial", 12, "bold"), bg="#1c1c1e", fg="white")
lbl_album.pack(pady=(10, 2))

lbl_artista = tk.Label(frame_arriba, font=("Arial", 12), bg="#1c1c1e", fg="#FF2A3C")
lbl_artista.pack(pady=(0, 10))

btn_reproducir = tk.Button(frame_arriba, text="▶ Reproducir", font=("Arial", 14), bg="#FF2A3C", fg="white", width=12, command=reproducir)
btn_reproducir.pack_forget()

# Lista de canciones
canvas_frame = tk.Frame(root, bg="#1c1c1e", height=230)
canvas_frame.pack_propagate(False)

# Scrollbar oscuro
style = ttk.Style()
style.theme_use('clam')
style.configure("Vertical.TScrollbar",
    background="#3a3a3c", darkcolor="#3a3a3c", lightcolor="#3a3a3c",
    troughcolor="#1c1c1e", bordercolor="#1c1c1e", arrowcolor="white"
)

canvas = tk.Canvas(canvas_frame, bg="#232324", highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

frame_canciones = tk.Frame(canvas, bg="#232324")
canvas.create_window((0, 0), window=frame_canciones, anchor="nw")
frame_canciones.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Vista canción sonando
frame_reproduciendo = tk.Frame(root, bg="#2c2c2e", height=50)
frame_reproduciendo.pack_forget()

lbl_repro_img = tk.Label(frame_reproduciendo, bg="#2c2c2e")
lbl_repro_img.pack(side="left", padx=10)

lbl_repro_titulo = tk.Label(frame_reproduciendo, text="", bg="#2c2c2e", font=("Arial", 10), fg="white")
lbl_repro_titulo.pack(side="left")

# Controles
frame_inferior = tk.Frame(root, bg="#1c1c1e")
frame_inferior.pack_forget()

frame_botones = tk.Frame(frame_inferior, bg="#1c1c1e")
frame_botones.pack()

btn_ret = tk.Button(frame_botones, text="⏮", font=("Arial", 10), bg="#3a3a3c", fg="white", command=lambda: cambiar_cancion(-1))
btn_ret.pack(side="left", padx=10)

btn_det = tk.Button(frame_botones, text="■", font=("Arial", 10), width=3, bg="#3a3a3c", fg="white", command=detener)
btn_det.pack(side="left", padx=10)

btn_sig = tk.Button(frame_botones, text="⏭", font=("Arial", 10), bg="#3a3a3c", fg="white", command=lambda: cambiar_cancion(1))
btn_sig.pack(side="left", padx=10)

btn_cargar = tk.Button(root, text="Biblioteca", font=("Arial", 12), command=biblioteca, bg="#3a3a3c", fg="white")
btn_cargar.pack(pady=(450, 20))

# Ejecutar
root.mainloop()
