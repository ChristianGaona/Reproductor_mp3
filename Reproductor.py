# Ejecutar en terminal estos comandos uno por uno
# pip install pillow
# pip install pygame
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import pygame
import os

pygame.mixer.init()

root = tk.Tk()
root.title("Reproductor")
root.geometry("400x700")
root.configure(bg="white")

lista_canciones = []
indice_actual = 0
portada_mini = None

# Parte superior
frame_arriba = tk.Frame(root, bg="white")
frame_arriba.pack(pady=10)

lbl_portada = tk.Label(frame_arriba, bg="white")
lbl_portada.pack()

lbl_album = tk.Label(frame_arriba, font=("Arial", 12, "bold"), bg="white")
lbl_album.pack(pady=(10, 2))

lbl_artista = tk.Label(frame_arriba, font=("Arial", 12), bg="white")
lbl_artista.pack(pady=(0, 10))

btn_reproducir = tk.Button(
    frame_arriba, text="▶ Reproducir", font=("Arial", 14),
    bg="#1DB954", fg="white", width=12, command=lambda: reproducir()
)
btn_reproducir.pack_forget()

# Lista de canciones
canvas_frame = tk.Frame(root, bg="white", height=280)
canvas_frame.pack_propagate(False)

canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

frame_canciones = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=frame_canciones, anchor="nw")

frame_canciones.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Vista canción sonando
frame_reproduciendo = tk.Frame(root, bg="#e3e1e1", height=50)
frame_reproduciendo.pack_forget()

lbl_repro_img = tk.Label(frame_reproduciendo, bg="#e3e1e1")
lbl_repro_img.pack(side="left", padx=10)

lbl_repro_titulo = tk.Label(frame_reproduciendo, text="", bg="#e3e1e1", font=("Arial", 10))
lbl_repro_titulo.pack(side="left")

# Controles 
frame_inferior = tk.Frame(root, bg="white")
frame_inferior.pack_forget()

frame_botones = tk.Frame(frame_inferior, bg="white")
frame_botones.pack()

btn_ret = tk.Button(frame_botones, text="⏮", font=("Arial", 10), command=lambda: cambiar_cancion(-1), bg="#f0f0f0")
btn_ret.pack(side="left", padx=10)

btn_det = tk.Button(frame_botones, text="■", font=("Arial", 10), command=lambda: detener(), bg="#f0f0f0", fg="black", width=3)
btn_det.pack(side="left", padx=10)

btn_sig = tk.Button(frame_botones, text="⏭", font=("Arial", 10), command=lambda: cambiar_cancion(1), bg="#f0f0f0")
btn_sig.pack(side="left", padx=10)

def reproducir():
    if lista_canciones:
        try:
            pygame.mixer.music.load(lista_canciones[indice_actual])
            pygame.mixer.music.play()
            lbl_repro_titulo.config(text=os.path.basename(lista_canciones[indice_actual]))
            if portada_mini:
                lbl_repro_img.config(image=portada_mini)
                lbl_repro_img.image = portada_mini
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir:\n{e}")

def detener():
    pygame.mixer.music.stop()
    lbl_repro_titulo.config(text="")
    lbl_repro_img.config(image="")

def cambiar_cancion(direccion):
    global indice_actual
    if lista_canciones:
        indice_actual = (indice_actual + direccion) % len(lista_canciones)
        reproducir()

def biblioteca():
    global lista_canciones, indice_actual, portada_mini
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

        lista_canciones = [os.path.join(carpeta, c["archivo"]) for c in datos["canciones"]]
        indice_actual = 0

        for i, cancion in enumerate(datos["canciones"], 1):
            fila = tk.Frame(frame_canciones, bg="white")
            fila.pack(anchor="w", pady=2, padx=10, fill="x")

            tk.Label(fila, text=f"{i}.", font=("Arial", 10), bg="white", width=3).pack(side="left")
            lbl_mini = tk.Label(fila, image=portada_mini, bg="white")
            lbl_mini.image = portada_mini
            lbl_mini.pack(side="left", padx=(0, 5))
            tk.Label(fila, text=f"{cancion['titulo']} ({cancion['duracion']})", font=("Arial", 10), bg="white", anchor="w").pack(side="left")

        btn_cargar.pack_forget()
        frame_reproduciendo.pack(after=canvas_frame, fill="x")
        frame_inferior.pack(side="bottom", fill="x", pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

btn_cargar = tk.Button(root, text="Biblioteca", font=("Arial", 12),
    command=biblioteca, bg="#f0f0f0", fg="black")
btn_cargar.pack(pady=(450, 20))

root.mainloop()
