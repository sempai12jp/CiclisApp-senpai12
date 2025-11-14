import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.data.colores import COLORES
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.data.colores import COLORES
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle

class WidgetMapaMejorado(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.marcadores = []
        self.rutas = []
        self.incidentes = []
        self.ubicacion_usuario = None
        self.lat_min, self.lat_max = -38.75, -38.72
        self.lon_min, self.lon_max = -72.61, -72.57
        self.bind(size=self.actualizar_graficos)
    def coord_a_pantalla(self, lat, lon):
        if self.size[0] == 0 or self.size[1] == 0:
            return 50, 50
        x_norm = (lon - self.lon_min) / (self.lon_max - self.lon_min)
        y_norm = (lat - self.lat_min) / (self.lat_max - self.lat_min)
        margen = 20
        x = self.x + margen + x_norm * (self.width - 2 * margen)
        y = self.y + margen + y_norm * (self.height - 2 * margen)
        return x, y
    def agregar_marcador(self, lat, lon, color=None, tipo="ubicacion"):
        if color is None:
            color = COLORES['peligro']
        self.marcadores.append((lat, lon, color, tipo))
        self.actualizar_graficos()
    def agregar_ruta(self, coordenadas, color=None):
        if color is None:
            color = COLORES['principal']
        self.rutas.append((coordenadas, color))
        self.actualizar_graficos()
    def agregar_incidente(self, lat, lon, tipo_incidente):
        self.incidentes.append((lat, lon, tipo_incidente))
        self.actualizar_graficos()
    def limpiar_todo(self):
        self.marcadores = []
        self.rutas = []
        self.incidentes = []
        self.actualizar_graficos()
    def actualizar_graficos(self, *args):
        self.canvas.clear()
        if self.size[0] == 0 or self.size[1] == 0:
            return
        with self.canvas:
            Color(0.85, 0.92, 0.98, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(*COLORES['texto_secundario'])
            Line(rectangle=(*self.pos, *self.size), width=2)
            Color(0.9, 0.9, 0.9, 0.7)
            for i in range(5):
                y_pos = self.y + (i + 1) * self.height / 6
                Line(points=[self.x + 15, y_pos, self.x + self.width - 15, y_pos], width=1)
            for i in range(5):
                x_pos = self.x + (i + 1) * self.width / 6
                Line(points=[x_pos, self.y + 15, x_pos, self.y + self.height - 15], width=1)
            for coordenadas, color_ruta in self.rutas:
                if len(coordenadas) < 2:
                    continue
                Color(0.3, 0.3, 0.3, 0.2)
                puntos = []
                for lat, lon in coordenadas:
                    x, y = self.coord_a_pantalla(lat, lon)
                    puntos.extend([x + 2, y - 2])
                if len(puntos) >= 4:
                    Line(points=puntos, width=6)
                Color(*color_ruta)
                puntos = []
                for lat, lon in coordenadas:
                    x, y = self.coord_a_pantalla(lat, lon)
                    puntos.extend([x, y])
                if len(puntos) >= 4:
                    Line(points=puntos, width=5, cap='round', joint='round')
            for lat, lon, tipo_incidente in self.incidentes:
                x, y = self.coord_a_pantalla(lat, lon)
                Color(0, 0, 0, 0.2)
                Ellipse(pos=(x - 12, y - 14), size=(24, 24))
                if tipo_incidente == "peligro":
                    color = COLORES['peligro']
                elif tipo_incidente == "reparacion":
                    color = COLORES['advertencia']
                else:
                    color = COLORES['secundario']
                Color(*color)
                Ellipse(pos=(x - 10, y - 10), size=(20, 20))
                Color(1, 1, 1, 1)
                Line(points=[x, y-5, x, y+2], width=2)
                Ellipse(pos=(x - 1, y + 3), size=(2, 2))
            for lat, lon, color_marcador, tipo_marcador in self.marcadores:
                x, y = self.coord_a_pantalla(lat, lon)
                Color(0, 0, 0, 0.3)
                Ellipse(pos=(x - 12, y - 14), size=(24, 24))
                Color(*color_marcador)
                if tipo_marcador == "usuario":
                    Ellipse(pos=(x - 12, y - 12), size=(24, 24))
                    Color(1, 1, 1, 1)
                    Ellipse(pos=(x - 8, y - 8), size=(16, 16))
                    Color(*color_marcador)
                    Ellipse(pos=(x - 4, y - 4), size=(8, 8))
                else:
                    Ellipse(pos=(x - 10, y - 10), size=(20, 20))
                    Color(1, 1, 1, 1)
                    Line(circle=(x, y, 10), width=2)