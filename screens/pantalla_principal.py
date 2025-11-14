from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, OneLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.colores import COLORES
from data.rutas import rutas_seguras

consejos_seguridad = [
    {"titulo": "Usa casco", "descripcion": "El casco reduce el riesgo de lesiones graves.", "icono": "bike-helmet"},
    {"titulo": "Respeta las señales", "descripcion": "Obedece semáforos y señales de tránsito.", "icono": "traffic-light"},
    {"titulo": "Mantén tu bici", "descripcion": "Revisa frenos y neumáticos antes de salir.", "icono": "wrench"},
    {"titulo": "Ilumina tu camino", "descripcion": "Usa luces y reflectantes en la noche.", "icono": "flashlight"},
    {"titulo": "Evita distracciones", "descripcion": "No uses el celular mientras pedaleas.", "icono": "cellphone"},
    {"titulo": "Planifica tu ruta", "descripcion": "Elige rutas seguras y conocidas.", "icono": "map-marker"},
]

class PantallaPrincipal(MDScreen):
    def __init__(self, **kwargs):
    # Archivo eliminado. Usar app/screens/pantalla_principal.py
        self.add_widget(layout)
        # ...rest of PantallaPrincipal code (tabs, consejos, config, actions)...
    # ...existing methods from main.py PantallaPrincipal...
    def mostrar_ubicacion(self, instance):
        lat, lon = -38.7359, -72.5904
        self.mapa.limpiar_todo()
        self.mapa.agregar_marcador(lat, lon, COLORES['exito'], "usuario")
        Snackbar(text="Ubicación actual mostrada").open()
    def mostrar_ruta_segura(self, instance):
        ruta_nombre = random.choice(list(rutas_seguras.keys()))
        coordenadas = rutas_seguras[ruta_nombre].get("coordenadas", [])
        self.mapa.agregar_ruta(coordenadas, COLORES['principal'])
        Snackbar(text=f"Mostrando: {ruta_nombre}").open()
    def seleccionar_ruta(self, nombre_ruta):
        info_ruta = rutas_seguras.get(nombre_ruta, {})
        coordenadas = info_ruta.get("coordenadas", [])
        self.mapa.limpiar_todo()
        self.mapa.agregar_ruta(coordenadas, COLORES['principal'])
        if len(coordenadas) >= 2:
            self.mapa.agregar_marcador(coordenadas[0][0], coordenadas[0][1], COLORES['exito'], "inicio")
            self.mapa.agregar_marcador(coordenadas[-1][0], coordenadas[-1][1], COLORES['peligro'], "fin")
        Snackbar(text=f"Ruta seleccionada: {nombre_ruta}").open()
    def reportar_problema(self, instance):
        lat = random.uniform(-38.75, -38.72)
        lon = random.uniform(-72.61, -72.57)
        tipo = random.choice(["peligro", "reparacion", "obstruccion"])
        self.mapa.agregar_incidente(lat, lon, tipo)
        tipos_texto = {
            "peligro": "Peligro reportado",
            "reparacion": "Reparación necesaria",
            "obstruccion": "Obstrucción reportada"
        }
        Snackbar(text=tipos_texto[tipo]).open()
    def limpiar_mapa(self, instance):
        self.mapa.limpiar_todo()
        Snackbar(text="Mapa limpiado").open()
    def mostrar_consejo_aleatorio(self, instance):
        consejo = random.choice(consejos_seguridad)
        self.label_consejo_aleatorio.text = consejo.get('descripcion', '')
        Snackbar(text=f"Consejo: {consejo.get('titulo', '')}").open()
    def cerrar_sesion(self, instance):
        def confirmar_logout(instance):
            self.manager.current = 'login'
            Snackbar(text="Sesión cerrada correctamente").open()
            dialog.dismiss()
        def cancelar_logout(instance):
            dialog.dismiss()
        # Diálogo de cierre de sesión
        label_dialog = MDLabel()
        label_dialog.theme_text_color = "Primary"
        label_dialog.text = "¿Estás seguro de que quieres cerrar la sesión?"
        dialog = MDDialog(
            title="Cerrar Sesión",
            content_cls=label_dialog,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=cancelar_logout,
                    theme_text_color="Custom",
                    text_color=COLORES['texto_secundario']
                ),
                MDRaisedButton(
                    text="CERRAR SESIÓN",
                    on_release=confirmar_logout,
                    md_bg_color=COLORES['peligro'],
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                ),
            ],
        )
        dialog.open()
