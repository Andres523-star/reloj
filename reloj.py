import tkinter as tk
from tkinter import ttk
import math
from datetime import datetime, timedelta

class RelojMinimalista:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj de Eventos")
        self.root.resizable(False, False)
        self.root.configure(bg="#F5F5F5")
        
        self.size = 500
        self.centro = self.size // 2
        self.radio = 200
        
        self.eventos = []
        self.evento_seleccionado = None
        self.es_24_horas = True
        
        self.coords_eventos = []
        self.hover_event = None
        
        self.paleta_tiempo = [
            (0, (30, 41, 59)),      # 00:00 - Gris azulado oscuro
            (6, (253, 230, 138)),   # 06:00 - Amarillo suave
            (12, (224, 242, 254)),  # 12:00 - Azul muy claro
            (18, (253, 186, 116)),  # 18:00 - Naranja suave
            (20, (71, 85, 105)),    # 20:00 - Gris azulado
            (24, (30, 41, 59))      # 24:00 - Vuelve a oscuro
        ]

        self.construir_interfaz()
        self.agregar_eventos_iniciales()
        self.actualizar_reloj()

    def construir_interfaz(self):
        self.frame_principal = tk.Frame(self.root, bg="#F5F5F5", padx=20, pady=20)
        self.frame_principal.pack()

        self.canvas = tk.Canvas(
            self.frame_principal, width=self.size, height=self.size, 
            bg="#F5F5F5", highlightthickness=0
        )
        self.canvas.pack()
        
        self.canvas.bind("<Motion>", self.detectar_mouse)

        self.frame_hora_digital = tk.Frame(self.frame_principal, bg="#F5F5F5")
        self.frame_hora_digital.pack(pady=5)
        
        self.combo_formato = ttk.Combobox(self.frame_hora_digital, values=["24 Horas", "12 Horas (AM/PM)"], state="readonly", width=15, font=("Helvetica", 10))
        self.combo_formato.set("24 Horas")
        self.combo_formato.pack(side="left", padx=5)
        self.combo_formato.bind("<<ComboboxSelected>>", self.cambiar_formato_hora)

        self.panel = tk.Frame(self.frame_principal, bg="#F5F5F5", pady=10)
        self.panel.pack(fill="x")

        self.lbl_hora = tk.Label(self.panel, text="Hora:", bg="#F5F5F5", font=("Helvetica", 11))
        self.lbl_hora.grid(row=0, column=0, padx=5)
        
        self.spin_hora = ttk.Spinbox(self.panel, from_=0, to=23, width=3, wrap=True, format="%02.0f", font=("Helvetica", 11))
        self.spin_hora.grid(row=0, column=1, padx=2)

        tk.Label(self.panel, text=":", bg="#F5F5F5", font=("Helvetica", 12, "bold")).grid(row=0, column=2)

        self.spin_minuto = ttk.Spinbox(self.panel, from_=0, to=59, width=3, wrap=True, format="%02.0f", font=("Helvetica", 11))
        self.spin_minuto.grid(row=0, column=3, padx=2)

        self.combo_ampm = ttk.Combobox(self.panel, values=["AM", "PM"], width=3, state="readonly", font=("Helvetica", 11))
        self.combo_ampm.grid(row=0, column=4, padx=2)
        self.combo_ampm.set("AM")
        self.combo_ampm.grid_remove() 

        self.lbl_texto = tk.Label(self.panel, text="Recordatorio:", bg="#F5F5F5", font=("Helvetica", 11))
        self.lbl_texto.grid(row=0, column=5, padx=(10, 5))
        
        self.entry_texto = ttk.Entry(self.panel, width=20, font=("Helvetica", 11))
        self.entry_texto.grid(row=0, column=6, padx=5)
        
        self.spin_hora.bind("<Return>", lambda e: self.guardar_evento())
        self.spin_minuto.bind("<Return>", lambda e: self.guardar_evento())
        self.entry_texto.bind("<Return>", lambda e: self.guardar_evento())

        self.frame_botones = tk.Frame(self.panel, bg="#F5F5F5")
        self.frame_botones.grid(row=1, column=0, columnspan=7, pady=10)

        self.btn_accion = ttk.Button(self.frame_botones, text="Agregar Evento", command=self.guardar_evento)
        self.btn_accion.pack(side="left", padx=5)

        self.btn_nuevo = ttk.Button(self.frame_botones, text="Cancelar/Nuevo", command=self.reset_formulario)
        self.btn_nuevo.pack(side="left", padx=5)

        self.btn_eliminar = ttk.Button(self.frame_botones, text="Eliminar", command=self.eliminar_evento)
        self.btn_eliminar.pack(side="left", padx=5)

        self.lista_eventos = tk.Listbox(
            self.panel, height=4, font=("Helvetica", 11), 
            bg="#FFFFFF", selectmode=tk.SINGLE, borderwidth=1, relief="solid"
        )
        self.lista_eventos.grid(row=2, column=0, columnspan=7, pady=5, sticky="ew")
        self.lista_eventos.bind("<<ListboxSelect>>", self.cargar_evento_seleccionado)

        self.lbl_mensaje = tk.Label(self.panel, text="", bg="#F5F5F5", font=("Helvetica", 10, "bold"))
        self.lbl_mensaje.grid(row=3, column=0, columnspan=7)

        self.reset_formulario()

    def cambiar_formato_hora(self, event=None):
        formato = self.combo_formato.get()
        if formato == "24 Horas":
            self.es_24_horas = True
            self.spin_hora.config(from_=0, to=23)
            self.combo_ampm.grid_remove()
        else:
            self.es_24_horas = False
            self.spin_hora.config(from_=1, to=12)
            self.combo_ampm.grid()
            
        self.refrescar_lista()
        self.reset_formulario()

    def agregar_eventos_iniciales(self):
        ahora = datetime.now()
        min1 = (ahora + timedelta(minutes=2)).strftime("%H:%M")
        min2 = (ahora + timedelta(minutes=3)).strftime("%H:%M")
        
        self.eventos = [
            {"hora": min1, "texto": "Prueba 1 (2 min)", "notificado": False},
            {"hora": min2, "texto": "Prueba 2 (3 min)", "notificado": False},
            {"hora": "14:30", "texto": "Almuerzo", "notificado": False}
        ]
        self.refrescar_lista()

    def obtener_hora_24h(self):
        h_str = self.spin_hora.get().strip()
        h = int(h_str) if h_str else 0
        m_str = self.spin_minuto.get().strip()
        m = int(m_str) if m_str else 0

        if self.es_24_horas:
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError("Hora fuera de rango (0-23).")
            return f"{h:02d}:{m:02d}"
        else:
            if not (1 <= h <= 12 and 0 <= m <= 59):
                raise ValueError("Hora fuera de rango (1-12).")
            ampm = self.combo_ampm.get()
            if ampm == "AM":
                if h == 12: h = 0 
            else: 
                if h != 12: h += 12 
            return f"{h:02d}:{m:02d}"

    def guardar_evento(self):
        texto = self.entry_texto.get().strip()

        if not texto:
            self.lbl_mensaje.config(text="¡Papi, escribe el título del recordatorio!", fg="#D32F2F")
            return
        
        # LÍMITE MÁXIMO DE 10 RECORDATORIOS
        if self.evento_seleccionado is None and len(self.eventos) >= 10:
            self.lbl_mensaje.config(text="¡Límite alcanzado! Máximo 10 recordatorios.", fg="#D32F2F")
            return
        
        try:
            hora_24 = self.obtener_hora_24h()
        except ValueError as e:
            self.lbl_mensaje.config(text=str(e), fg="#D32F2F")
            return

        if self.evento_seleccionado is not None:
            self.eventos[self.evento_seleccionado] = {"hora": hora_24, "texto": texto, "notificado": False}
            self.lbl_mensaje.config(text="Recordatorio actualizado.", fg="#388E3C")
        else:
            self.eventos.append({"hora": hora_24, "texto": texto, "notificado": False})
            self.lbl_mensaje.config(text="Recordatorio agregado.", fg="#388E3C")

        self.reset_formulario(silencioso=True)
        self.refrescar_lista()

    def eliminar_evento(self):
        if self.evento_seleccionado is not None:
            del self.eventos[self.evento_seleccionado]
            self.lbl_mensaje.config(text="Recordatorio eliminado.", fg="#D32F2F")
            self.reset_formulario(silencioso=True)
            self.refrescar_lista()
        else:
            self.lbl_mensaje.config(text="Selecciona un recordatorio de la lista.", fg="#D32F2F")

    def cargar_evento_seleccionado(self, event):
        sel = self.lista_eventos.curselection()
        if sel:
            self.evento_seleccionado = sel[0]
            ev = self.eventos[self.evento_seleccionado]
            h24, m = map(int, ev["hora"].split(":"))
            
            if self.es_24_horas:
                self.spin_hora.set(f"{h24:02d}")
            else:
                ampm = "AM" if h24 < 12 else "PM"
                h12 = h24 % 12
                if h12 == 0: h12 = 12
                self.spin_hora.set(f"{h12:02d}")
                self.combo_ampm.set(ampm)
                
            self.spin_minuto.set(f"{m:02d}")
            self.entry_texto.delete(0, tk.END)
            self.entry_texto.insert(0, ev["texto"])
            
            self.btn_accion.config(text="Guardar Cambios")
            self.lbl_mensaje.config(text="Editando recordatorio...", fg="#1976D2")

    def reset_formulario(self, silencioso=False):
        self.spin_hora.set("")
        self.spin_minuto.set("")
        self.combo_ampm.set("AM")
        self.entry_texto.delete(0, tk.END)
        
        self.evento_seleccionado = None
        self.lista_eventos.selection_clear(0, tk.END)
        self.btn_accion.config(text="Agregar Evento")
        
        if not silencioso:
            self.lbl_mensaje.config(text="")

    def refrescar_lista(self):
        self.eventos.sort(key=lambda x: x["hora"])
        self.lista_eventos.delete(0, tk.END)
        for ev in self.eventos:
            h24, m = map(int, ev["hora"].split(":"))
            if self.es_24_horas:
                hora_str = f"{h24:02d}:{m:02d}"
            else:
                ampm = "AM" if h24 < 12 else "PM"
                h12 = h24 % 12
                if h12 == 0: h12 = 12
                hora_str = f"{h12:02d}:{m:02d} {ampm}"
                
            self.lista_eventos.insert(tk.END, f"{hora_str}  -  {ev['texto']}")

    def mostrar_alerta(self, evento):
        alerta = tk.Toplevel(self.root)
        alerta.title("Recordatorio")
        alerta.geometry("320x180")
        alerta.configure(bg="#FFFFFF")
        alerta.resizable(False, False)
        
        alerta.transient(self.root) 
        alerta.grab_set()
        alerta.update_idletasks() 
        
        tk.Label(alerta, text="¡RECORDATORIO!", bg="#FFFFFF", fg="#D32F2F", font=("Helvetica", 14, "bold")).pack(pady=(20, 5))
        tk.Label(alerta, text=evento["texto"], bg="#FFFFFF", fg="#333333", font=("Helvetica", 13), wraplength=280).pack(pady=10)

        frame_btns = tk.Frame(alerta, bg="#FFFFFF")
        frame_btns.pack(pady=10)

        btn_ok = ttk.Button(frame_btns, text="OK", command=alerta.destroy)
        btn_ok.pack(side="left", padx=10)

        def posponer():
            h, m = map(int, evento["hora"].split(":"))
            tiempo_evento = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
            tiempo_nuevo = tiempo_evento + timedelta(minutes=10)
            evento["hora"] = tiempo_nuevo.strftime("%H:%M")
            evento["notificado"] = False
            self.refrescar_lista()
            alerta.destroy()

        btn_posponer = ttk.Button(frame_btns, text="Posponer 10 min", command=posponer)
        btn_posponer.pack(side="left", padx=10)

    def obtener_color_fondo(self, ahora):
        t = ahora.hour + ahora.minute / 60.0
        for i in range(len(self.paleta_tiempo) - 1):
            h_ini, c_ini = self.paleta_tiempo[i]
            h_fin, c_fin = self.paleta_tiempo[i + 1]
            if h_ini <= t <= h_fin:
                prog = (t - h_ini) / (h_fin - h_ini)
                r = int(c_ini[0] + (c_fin[0] - c_ini[0]) * prog)
                g = int(c_ini[1] + (c_fin[1] - c_ini[1]) * prog)
                b = int(c_ini[2] + (c_fin[2] - c_ini[2]) * prog)
                return f"#{r:02x}{g:02x}{b:02x}"
        return "#E0F2FE"

    def calcular_coordenadas(self, angulo, radio):
        rad = math.radians(angulo)
        x = self.centro + radio * math.sin(rad)
        y = self.centro - radio * math.cos(rad)
        return x, y

    def detectar_mouse(self, event):
        hover_encontrado = None
        for ev, ex, ey in self.coords_eventos:
            distancia = math.hypot(event.x - ex, event.y - ey)
            if distancia < 40:
                hover_encontrado = ev
                break
        
        if hover_encontrado != self.hover_event:
            self.hover_event = hover_encontrado
            self.dibujar_reloj(datetime.now())

    def dibujar_tooltip(self, ev):
        h, m = map(int, ev["hora"].split(":"))
        ang_ev = (h % 12) * 30 + (m / 60) * 30
        x_t, y_t = self.calcular_coordenadas(ang_ev, self.radio - 120)
        
        if self.es_24_horas:
            hora_str = f"{h:02d}:{m:02d}"
        else:
            ampm = "AM" if h < 12 else "PM"
            h12 = h % 12
            if h12 == 0: h12 = 12
            hora_str = f"{h12:02d}:{m:02d} {ampm}"

        texto = f"{hora_str} - {ev['texto']}"
        temp_id = self.canvas.create_text(x_t, y_t, text=texto, font=("Helvetica", 10, "bold"), tags="tooltip")
        bbox = self.canvas.bbox(temp_id)
        
        if bbox:
            x1, y1, x2, y2 = bbox
            x1 -= 8; y1 -= 4; x2 += 8; y2 += 4
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FFFFFF", outline="#888888", width=2, tags="tooltip")
            self.canvas.tag_raise(temp_id)
            self.canvas.itemconfig(temp_id, fill="#1A1A1A")

    def dibujar_reloj(self, ahora):
        self.canvas.delete("all")
        color_fondo = self.obtener_color_fondo(ahora)
        
        self.canvas.create_oval(
            self.centro - self.radio, self.centro - self.radio,
            self.centro + self.radio, self.centro + self.radio,
            fill=color_fondo, outline="#333333", width=6 
        )

        r = int(color_fondo[1:3], 16)
        g = int(color_fondo[3:5], 16)
        b = int(color_fondo[5:7], 16)
        brillo = (r * 299 + g * 587 + b * 114) / 1000
        c_texto = "#1A1A1A" if brillo > 140 else "#F8F9FA"
        c_linea = "#777777" if brillo > 140 else "#A0AAB5"

        for h in range(1, 13):
            ang = h * 30
            x_t, y_t = self.calcular_coordenadas(ang, self.radio - 25)
            self.canvas.create_text(x_t, y_t, text=f"{h}", fill=c_texto, font=("Helvetica", 14, "bold"))

        self.coords_eventos = []

        for i, ev in enumerate(self.eventos):
            try:
                h, m = map(int, ev["hora"].split(":"))
                ang_ev = (h % 12) * 30 + (m / 60) * 30
                
                x_ini, y_ini = self.calcular_coordenadas(ang_ev, 40)
                x_fin, y_fin = self.calcular_coordenadas(ang_ev, self.radio - 10)
                self.canvas.create_line(x_ini, y_ini, x_fin, y_fin, fill=c_linea, width=1)
                
                x_p, y_p = self.calcular_coordenadas(ang_ev, self.radio - 10)
                self.canvas.create_oval(x_p-3, y_p-3, x_p+3, y_p+3, fill=c_texto, outline="")

                radio_texto = self.radio - 65
                if i % 2 == 1:
                    radio_texto -= 25 

                x_ev, y_ev = self.calcular_coordenadas(ang_ev, radio_texto)
                
                rot = -ang_ev + 90
                if 90 < ang_ev < 270:
                    rot += 180
                
                texto_corto = ev["texto"][:12] + "..." if len(ev["texto"]) > 12 else ev["texto"]
                
                self.canvas.create_text(x_ev, y_ev, text=texto_corto, fill=c_texto, font=("Helvetica", 8, "bold"), angle=rot)
                
                self.coords_eventos.append((ev, x_ev, y_ev))
                
            except:
                pass

        ang_h = ((ahora.hour % 12) + ahora.minute / 60) * 30
        x_h, y_h = self.calcular_coordenadas(ang_h, self.radio - 90)
        self.canvas.create_line(self.centro, self.centro, x_h, y_h, fill="#222222" if brillo > 140 else "#E2E8F0", width=8, capstyle="round")

        ang_m = (ahora.minute + ahora.second / 60) * 6
        x_m, y_m = self.calcular_coordenadas(ang_m, self.radio - 40)
        self.canvas.create_line(self.centro, self.centro, x_m, y_m, fill="#222222" if brillo > 140 else "#E2E8F0", width=5, capstyle="round")

        ang_s = ahora.second * 6
        x_s, y_s = self.calcular_coordenadas(ang_s, self.radio - 15)
        self.canvas.create_line(self.centro, self.centro, x_s, y_s, fill="#E53935", width=2, capstyle="round")

        self.canvas.create_oval(self.centro - 6, self.centro - 6, self.centro + 6, self.centro + 6, fill="#333333" if brillo > 140 else "#FFFFFF", outline="")

        h_digital = ahora.strftime("%H:%M:%S") if self.es_24_horas else ahora.strftime("%I:%M:%S %p")
        self.canvas.create_text(self.centro, self.centro + 80, text=h_digital, fill=c_texto, font=("Consolas", 16, "bold"))

        if self.hover_event:
            self.dibujar_tooltip(self.hover_event)

    def actualizar_reloj(self):
        ahora = datetime.now()
        self.dibujar_reloj(ahora)
        
        hora_actual = ahora.strftime("%H:%M")
        for ev in self.eventos:
            if ev["hora"] == hora_actual and not ev.get("notificado", False):
                self.mostrar_alerta(ev)
                ev["notificado"] = True 
        
        self.root.after(1000, self.actualizar_reloj)

if __name__ == "__main__":
    ventana = tk.Tk()
    app = RelojMinimalista(ventana)
    ventana.mainloop()