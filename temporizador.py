import tkinter as tk
from tkinter import font
import threading
from pynput.keyboard import Listener as KeyListener, Key
import sys

# Configuración de atajos - cambiar aquí si tus teclas no son F14/F15
TECLA_INICIAR = Key.f14  # Cambiar a Key.f13, Key.f12, etc. si es necesario
TECLA_REINICIAR = Key.f15  # Cambiar a otro Key si es necesario

class Temporizador:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Temporizador")
        self.ventana.geometry("180x65+500+300")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#f0f0f0")
        
        # Centrar ventana en pantalla
        self.ventana.update_idletasks()
        ancho_ventana = self.ventana.winfo_width()
        alto_ventana = self.ventana.winfo_height()
        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)
        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
        
        self.ventana.attributes('-topmost', True)
        self.ventana.attributes('-alpha', 0.7)
        
        print("[TEMPORIZADOR] Ventana inicializada")
        print(f"[TEMPORIZADOR] Sistema operativo: {sys.platform}")

        # Variables de estado
        self.tiempo_restante = 60
        self.activo = False
        self._job = None
        self._job_frente = None
        self.keyboard_listener = None
        self._lock = threading.Lock()

        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar)

        # Listener global del teclado - funciona en segundo plano
        try:
            self.keyboard_listener = KeyListener(on_press=self._on_key_press)
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            print(f"[TEMPORIZADOR] Listener global de teclado activo")
            print(f"[TEMPORIZADOR] Teclas globales:")
            print(f"  - {TECLA_INICIAR}: Iniciar temporizador")
            print(f"  - {TECLA_REINICIAR}: Reiniciar temporizador")
        except Exception as e:
            print(f"[TEMPORIZADOR] Advertencia: No se pudo iniciar listener global: {e}")
            print("[TEMPORIZADOR] Los atajos globales NO funcionarán, pero puedes usar la ventana")

        # Mantener siempre en primer plano
        self.ventana.attributes('-topmost', True)
        self._mantener_en_frente()
        
        # UI - Solo display del tiempo
        fuente_grande = font.Font(family="Helvetica", size=36, weight="bold")
        
        self.etiqueta_tiempo = tk.Label(
            ventana,
            text=self._formato(self.tiempo_restante),
            font=fuente_grande,
            fg="#FF6B6B",
            bg="#f0f0f0",
            padx=0,
            pady=0
        )
        self.etiqueta_tiempo.pack(fill=tk.BOTH, expand=True)

        # Atajos cuando la ventana tiene foco
        self.ventana.bind("<F14>", lambda e: self.iniciar())
        self.ventana.bind("<F15>", lambda e: self.reiniciar())
        # Atajos alternativos
        self.ventana.bind("<Control-s>", lambda e: self.iniciar())  # Ctrl+S para iniciar
        self.ventana.bind("<Control-r>", lambda e: self.reiniciar())  # Ctrl+R para reiniciar
        self.ventana.bind("<space>", lambda e: self.iniciar())  # Espacio para iniciar
        
        print("[TEMPORIZADOR] Atajos de ventana:")
        print("[TEMPORIZADOR] F14 o Ctrl+S o Espacio: Iniciar")
        print("[TEMPORIZADOR] F15 o Ctrl+R: Reiniciar")

    def _formato(self, segundos):
        return f"{segundos // 60:02d}:{segundos % 60:02d}"

    def _mantener_en_frente(self):
        """Mantiene la ventana siempre en primer plano"""
        try:
            self.ventana.lift()
            self.ventana.attributes('-topmost', True)
        except:
            pass
        self._job_frente = self.ventana.after(200, self._mantener_en_frente)

    def _on_key_press(self, key):
        """Listener global del teclado - detecta F14 y F15 en cualquier lugar"""
        try:
            if key == TECLA_INICIAR:
                self.ventana.after(0, self.iniciar)
            elif key == TECLA_REINICIAR:
                self.ventana.after(0, self.reiniciar)
        except AttributeError:
            pass



    def iniciar(self):
        with self._lock:
            if self.activo:
                return
            self.activo = True
        print("[TEMPORIZADOR] Iniciando")
        self.ventana.lift()
        self.etiqueta_tiempo.config(fg="#FF6B6B")
        self._contar()

    def reiniciar(self):
        with self._lock:
            self.activo = False
            self.tiempo_restante = 60
        if self._job:
            self.ventana.after_cancel(self._job)
            self._job = None
        self.etiqueta_tiempo.config(text=self._formato(60), fg="#FF6B6B")
        print("[TEMPORIZADOR] Reiniciado")

    def _contar(self):
        with self._lock:
            if not self.activo:
                return
            if self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                restante = self.tiempo_restante
            else:
                restante = 0

        self.etiqueta_tiempo.config(text=self._formato(restante))

        if restante <= 10:
            self.etiqueta_tiempo.config(fg="#FF0000")
        else:
            self.etiqueta_tiempo.config(fg="#FF6B6B")

        if restante > 0:
            self._job = self.ventana.after(1000, self._contar)
        else:
            with self._lock:
                self.activo = False
            self.ventana.bell()
            print("[TEMPORIZADOR] ¡Tiempo terminado!")

    def _cerrar(self):
        if self._job:
            self.ventana.after_cancel(self._job)
        if self._job_frente:
            self.ventana.after_cancel(self._job_frente)
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.ventana.destroy()


if __name__ == "__main__":
    print("[TEMPORIZADOR] Iniciando aplicación...")
    ventana = tk.Tk()
    app = Temporizador(ventana)
    ventana.mainloop()
    print("[TEMPORIZADOR] Aplicación cerrada")
