from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton
from plyer import gps
from app.data.colores import COLORES
import requests
import threading

try:
    from kivy_garden.mapview import MapView, MapMarker, MapSource
    MAPVIEW_AVAILABLE = True
except ImportError:
    MAPVIEW_AVAILABLE = False
    print("MapView no disponible, usando mapa alternativo con tiles")


class MapaInteractivo(BoxLayout):
    """Mapa interactivo con GPS y marcadores para ciclovías."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.lat = -38.7359  # Temuco por defecto
        self.lon = -72.5904
        self.zoom = 13
        self.marcadores = []
        self.rutas = []
        self.ciclovias_reales = []  # Ciclovías obtenidas de OpenStreetMap
        self.ubicacion_usuario = None
        self.gps_enabled = False
        self.tiles_cache = {}
        self.ciclovias_cargadas = False
        
        # Configurar GPS
        self.configurar_gps()
        
        if MAPVIEW_AVAILABLE:
            self.crear_mapview()
        else:
            self.crear_mapa_alternativo()
        
        self.agregar_controles()
        
        # Cargar ciclovías reales en segundo plano
        self.cargar_ciclovias_reales()
        
    def configurar_gps(self):
        """Configura el GPS usando plyer."""
        try:
            # En Windows, el GPS puede no estar disponible
            # Intentamos configurarlo pero manejamos errores
            try:
                gps.configure(on_location=self.on_gps_location)
            except Exception:
                # En Windows/desarrollo, podemos simular ubicación
                # O usar ubicación por defecto de Temuco
                pass
        except Exception as e:
            print(f"GPS no disponible (normal en Windows/desarrollo): {e}")
    
    def on_gps_location(self, **kwargs):
        """Callback cuando se recibe una ubicación GPS."""
        try:
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            if lat and lon:
                self.ubicacion_usuario = (lat, lon)
                self.lat = lat
                self.lon = lon
                if MAPVIEW_AVAILABLE and hasattr(self, 'mapview'):
                    self.mapview.center_on(lat, lon)
                else:
                    self.actualizar_mapa()
        except Exception as e:
            print(f"Error procesando ubicación GPS: {e}")
    
    def crear_mapview(self):
        """Crea un mapa usando kivy-garden.mapview."""
        try:
            self.mapview = MapView(zoom=self.zoom, lat=self.lat, lon=self.lon)
            self.mapview.bind(on_map_relocated=self.on_map_moved)
            
            # Agregar marcador de usuario si hay GPS
            if self.ubicacion_usuario:
                marker = MapMarker(lat=self.ubicacion_usuario[0], 
                                  lon=self.ubicacion_usuario[1])
                self.mapview.add_marker(marker)
            
            # Agregar rutas seguras
            self.agregar_rutas_seguras()
            
            self.add_widget(self.mapview)
        except Exception as e:
            print(f"Error creando MapView: {e}")
            self.crear_mapa_alternativo()
    
    def crear_mapa_alternativo(self):
        """Crea un mapa alternativo usando tiles de OpenStreetMap."""
        # Widget de mapa personalizado
        self.mapa_widget = Widget()
        self.mapa_widget.bind(size=self.actualizar_mapa, pos=self.actualizar_mapa)
        self.add_widget(self.mapa_widget)
        
        # Cargar rutas seguras
        self.agregar_rutas_seguras()
        
        # Cargar mapa inicial
        Clock.schedule_once(lambda dt: self.actualizar_mapa(), 0.1)
    
    def actualizar_mapa(self, *args):
        """Actualiza el mapa alternativo."""
        if not hasattr(self, 'mapa_widget'):
            return
        
        self.mapa_widget.canvas.clear()
        
        with self.mapa_widget.canvas:
            # Fondo del mapa (simulando calles y áreas)
            Color(0.85, 0.90, 0.95, 1)
            Rectangle(pos=self.mapa_widget.pos, size=self.mapa_widget.size)
            
            # Dibujar cuadrícula de calles
            self.dibujar_cuadricula()
            
            # Dibujar rutas seguras
            self.dibujar_rutas()
            
            # Dibujar marcadores
            self.dibujar_marcadores()
            
            # Dibujar ubicación del usuario
            if self.ubicacion_usuario:
                self.dibujar_ubicacion_usuario()
    
    def dibujar_cuadricula(self):
        """Dibuja una cuadrícula simulando calles."""
        Color(0.75, 0.80, 0.85, 0.5)
        # Líneas horizontales
        for i in range(1, 6):
            y_pos = self.mapa_widget.y + (i * self.mapa_widget.height / 6)
            Line(points=[
                self.mapa_widget.x + dp(10), y_pos,
                self.mapa_widget.x + self.mapa_widget.width - dp(10), y_pos
            ], width=dp(1))
        
        # Líneas verticales
        for i in range(1, 6):
            x_pos = self.mapa_widget.x + (i * self.mapa_widget.width / 6)
            Line(points=[
                x_pos, self.mapa_widget.y + dp(10),
                x_pos, self.mapa_widget.y + self.mapa_widget.height - dp(10)
            ], width=dp(1))
    
    def dibujar_rutas(self):
        """Dibuja las rutas seguras en el mapa."""
        from app.data.rutas import rutas_seguras
        
        # Dibujar rutas predefinidas
        for nombre_ruta, info in rutas_seguras.items():
            coordenadas = info.get('coordenadas', [])
            if len(coordenadas) < 2:
                continue
            
            # Dibujar ruta predefinida
            Color(0.2, 0.6, 0.9, 0.8)
            puntos = []
            for lat, lon in coordenadas:
                x, y = self.coord_a_pantalla(lat, lon)
                puntos.extend([x, y])
            
            if len(puntos) >= 4:
                Line(points=puntos, width=dp(4), cap='round', joint='round')
        
        # Dibujar ciclovías reales de OpenStreetMap
        if self.ciclovias_reales:
            Color(0.1, 0.8, 0.3, 0.9)  # Verde para ciclovías reales
            for coordenadas in self.ciclovias_reales:
                if len(coordenadas) < 2:
                    continue
                
                puntos = []
                for lat, lon in coordenadas:
                    x, y = self.coord_a_pantalla(lat, lon)
                    puntos.extend([x, y])
                
                if len(puntos) >= 4:
                    Line(points=puntos, width=dp(5), cap='round', joint='round')
    
    def dibujar_marcadores(self):
        """Dibuja los marcadores en el mapa."""
        for lat, lon, color, tipo in self.marcadores:
            x, y = self.coord_a_pantalla(lat, lon)
            
            # Sombra
            Color(0, 0, 0, 0.3)
            Ellipse(pos=(x - dp(8), y - dp(8)), size=(dp(16), dp(16)))
            
            # Marcador
            Color(*color)
            Ellipse(pos=(x - dp(6), y - dp(6)), size=(dp(12), dp(12)))
            
            # Centro blanco
            Color(1, 1, 1, 1)
            Ellipse(pos=(x - dp(2), y - dp(2)), size=(dp(4), dp(4)))
    
    def dibujar_ubicacion_usuario(self):
        """Dibuja la ubicación del usuario."""
        if not self.ubicacion_usuario:
            return
        
        lat, lon = self.ubicacion_usuario
        x, y = self.coord_a_pantalla(lat, lon)
        
        # Círculo exterior animado
        Color(0.2, 0.7, 1.0, 0.3)
        Ellipse(pos=(x - dp(15), y - dp(15)), size=(dp(30), dp(30)))
        
        # Círculo medio
        Color(0.2, 0.7, 1.0, 0.5)
        Ellipse(pos=(x - dp(10), y - dp(10)), size=(dp(20), dp(20)))
        
        # Punto central
        Color(0.1, 0.5, 1.0, 1)
        Ellipse(pos=(x - dp(6), y - dp(6)), size=(dp(12), dp(12)))
        
        # Centro blanco
        Color(1, 1, 1, 1)
        Ellipse(pos=(x - dp(2), y - dp(2)), size=(dp(4), dp(4)))
    
    def coord_a_pantalla(self, lat, lon):
        """Convierte coordenadas geográficas a coordenadas de pantalla."""
        if not hasattr(self, 'mapa_widget'):
            return 0, 0
        
        # Rango de coordenadas de Temuco
        lat_min, lat_max = -38.75, -38.72
        lon_min, lon_max = -72.61, -72.57
        
        # Normalizar coordenadas
        x_norm = (lon - lon_min) / (lon_max - lon_min)
        y_norm = (lat - lat_min) / (lat_max - lat_min)
        
        # Convertir a píxeles
        margen = dp(20)
        x = self.mapa_widget.x + margen + x_norm * (self.mapa_widget.width - 2 * margen)
        y = self.mapa_widget.y + margen + y_norm * (self.mapa_widget.height - 2 * margen)
        
        return x, y
    
    def agregar_controles(self):
        """Agrega controles al mapa (botones de zoom, GPS, etc.)."""
        controles = BoxLayout(orientation='horizontal', 
                             size_hint_y=None, 
                             height=dp(50),
                             padding=dp(10),
                             spacing=dp(10))
        
        # Botón para activar/desactivar GPS
        self.btn_gps = MDIconButton(
            icon='crosshairs-gps',
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 0.9, 1),
            on_release=self.toggle_gps
        )
        controles.add_widget(self.btn_gps)
        
        # Botón para centrar en ubicación
        btn_centrar = MDIconButton(
            icon='target',
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 0.9, 1),
            on_release=self.centrar_en_ubicacion
        )
        controles.add_widget(btn_centrar)
        
        # Botón para agregar marcador
        btn_marcador = MDIconButton(
            icon='map-marker',
            theme_icon_color="Custom",
            icon_color=(0.9, 0.6, 0.2, 1),
            on_release=self.agregar_marcador_ubicacion
        )
        controles.add_widget(btn_marcador)
        
        # Botón para recargar ciclovías
        self.btn_recargar = MDIconButton(
            icon='refresh',
            theme_icon_color="Custom",
            icon_color=(0.1, 0.8, 0.3, 1),
            on_release=self.recargar_ciclovias
        )
        controles.add_widget(self.btn_recargar)
        
        self.add_widget(controles)
    
    def toggle_gps(self, instance):
        """Activa o desactiva el GPS."""
        try:
            if not self.gps_enabled:
                try:
                    gps.start(minTime=1000, minDistance=1)
                    self.gps_enabled = True
                    self.btn_gps.icon_color = (0.2, 0.9, 0.2, 1)  # Verde cuando está activo
                    from app.utils.ui import show_snackbar
                    show_snackbar("GPS activado", allow_on_login=True)
                except Exception as e:
                    # En Windows/desarrollo, simular ubicación
                    print(f"GPS no disponible, usando ubicación simulada: {e}")
                    self.ubicacion_usuario = (self.lat, self.lon)
                    self.gps_enabled = True
                    self.btn_gps.icon_color = (0.8, 0.8, 0.2, 1)  # Amarillo para simulado
                    from app.utils.ui import show_snackbar
                    show_snackbar("GPS simulado (Temuco)", allow_on_login=True)
                    self.actualizar_mapa()
            else:
                try:
                    gps.stop()
                except:
                    pass
                self.gps_enabled = False
                self.btn_gps.icon_color = (0.2, 0.6, 0.9, 1)  # Azul cuando está inactivo
                from app.utils.ui import show_snackbar
                show_snackbar("GPS desactivado", allow_on_login=True)
        except Exception as e:
            print(f"Error al activar GPS: {e}")
            from app.utils.ui import show_snackbar
            show_snackbar(f"Error GPS: {str(e)}", allow_on_login=True)
    
    def centrar_en_ubicacion(self, instance):
        """Centra el mapa en la ubicación del usuario."""
        if self.ubicacion_usuario:
            nueva_lat, nueva_lon = self.ubicacion_usuario
            # Si la ubicación cambió significativamente, recargar ciclovías
            if abs(nueva_lat - self.lat) > 0.01 or abs(nueva_lon - self.lon) > 0.01:
                self.lat = nueva_lat
                self.lon = nueva_lon
                self.cargar_ciclovias_reales()
            else:
                self.lat = nueva_lat
                self.lon = nueva_lon
            
            if MAPVIEW_AVAILABLE and hasattr(self, 'mapview'):
                self.mapview.center_on(self.lat, self.lon)
            else:
                self.actualizar_mapa()
        else:
            from app.utils.ui import show_snackbar
            show_snackbar("Ubicación GPS no disponible", allow_on_login=True)
    
    def agregar_marcador_ubicacion(self, instance):
        """Agrega un marcador en la ubicación actual."""
        if self.ubicacion_usuario:
            self.agregar_marcador(
                self.ubicacion_usuario[0],
                self.ubicacion_usuario[1],
                COLORES.get('principal', (0.2, 0.6, 0.9, 1)),
                "punto_interes"
            )
        else:
            from app.utils.ui import show_snackbar
            show_snackbar("Activa el GPS primero", allow_on_login=True)
    
    def agregar_marcador(self, lat, lon, color=None, tipo="ubicacion"):
        """Agrega un marcador al mapa."""
        if color is None:
            color = COLORES.get('peligro', (0.9, 0.2, 0.2, 1))
        
        self.marcadores.append((lat, lon, color, tipo))
        
        if MAPVIEW_AVAILABLE and hasattr(self, 'mapview'):
            marker = MapMarker(lat=lat, lon=lon)
            self.mapview.add_marker(marker)
        else:
            self.actualizar_mapa()
    
    def agregar_rutas_seguras(self):
        """Agrega las rutas seguras al mapa."""
        from app.data.rutas import rutas_seguras
        
        for nombre_ruta, info in rutas_seguras.items():
            coordenadas = info.get('coordenadas', [])
            if len(coordenadas) >= 2:
                self.rutas.append((coordenadas, COLORES.get('principal', (0.2, 0.6, 0.9, 1))))
        
        if not MAPVIEW_AVAILABLE:
            self.actualizar_mapa()
    
    def on_map_moved(self, *args):
        """Callback cuando el mapa se mueve."""
        if MAPVIEW_AVAILABLE and hasattr(self, 'mapview'):
            self.lat = self.mapview.lat
            self.lon = self.mapview.lon
            self.zoom = self.mapview.zoom
    
    def limpiar_marcadores(self):
        """Limpia todos los marcadores."""
        self.marcadores = []
        if MAPVIEW_AVAILABLE and hasattr(self, 'mapview'):
            self.mapview.clear_markers()
        else:
            self.actualizar_mapa()
    
    def cargar_ciclovias_reales(self):
        """Carga las ciclovías reales desde OpenStreetMap usando Overpass API."""
        def cargar_en_thread():
            try:
                # Área de búsqueda alrededor de Temuco (bounding box)
                # Expandimos un poco el área para obtener más ciclovías
                lat_min = self.lat - 0.05  # ~5.5 km
                lat_max = self.lat + 0.05
                lon_min = self.lon - 0.05
                lon_max = self.lon + 0.05
                
                # Query Overpass para obtener ciclovías
                # Buscamos ways con tags de ciclovías
                query = f"""
                [out:json][timeout:25];
                (
                  way["highway"="cycleway"]({lat_min},{lon_min},{lat_max},{lon_max});
                  way["bicycle"="designated"]({lat_min},{lon_min},{lat_max},{lon_max});
                  way["bicycle"="yes"]({lat_min},{lon_min},{lat_max},{lon_max});
                  way["cycleway"]({lat_min},{lon_min},{lat_max},{lon_max});
                );
                out geom;
                """
                
                # Hacer petición a Overpass API
                url = "https://overpass-api.de/api/interpreter"
                response = requests.post(url, data={'data': query}, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    ciclovias = []
                    
                    # Procesar los resultados
                    for element in data.get('elements', []):
                        if element.get('type') == 'way' and 'geometry' in element:
                            coordenadas = []
                            for point in element['geometry']:
                                lat = point['lat']
                                lon = point['lon']
                                coordenadas.append((lat, lon))
                            
                            if len(coordenadas) >= 2:
                                ciclovias.append(coordenadas)
                    
                    # Actualizar en el hilo principal
                    Clock.schedule_once(lambda dt: self.actualizar_ciclovias(ciclovias), 0)
                    
            except Exception as e:
                print(f"Error cargando ciclovías de OpenStreetMap: {e}")
                # Si falla, usar ciclovías de ejemplo basadas en ubicación
                Clock.schedule_once(lambda dt: self.agregar_ciclovias_ejemplo(), 0)
        
        # Ejecutar en un thread separado para no bloquear la UI
        thread = threading.Thread(target=cargar_en_thread, daemon=True)
        thread.start()
    
    def actualizar_ciclovias(self, ciclovias):
        """Actualiza las ciclovías en el mapa."""
        self.ciclovias_reales = ciclovias
        self.ciclovias_cargadas = True
        
        if not MAPVIEW_AVAILABLE:
            self.actualizar_mapa()
        
        from app.utils.ui import show_snackbar
        if ciclovias:
            show_snackbar(f"{len(ciclovias)} ciclovías cargadas", allow_on_login=True)
        else:
            show_snackbar("No se encontraron ciclovías en esta zona", allow_on_login=True)
    
    def agregar_ciclovias_ejemplo(self):
        """Agrega ciclovías de ejemplo si no se pueden cargar de OpenStreetMap."""
        # Ciclovías de ejemplo basadas en la ubicación de Temuco
        # Estas son aproximaciones de rutas comunes
        ejemplo_ciclovias = [
            # Ruta norte-sur aproximada
            [
                (-38.7359, -72.5904),
                (-38.7365, -72.5900),
                (-38.7370, -72.5895),
                (-38.7375, -72.5890)
            ],
            # Ruta este-oeste aproximada
            [
                (-38.7350, -72.5900),
                (-38.7355, -72.5910),
                (-38.7360, -72.5920),
                (-38.7365, -72.5930)
            ],
            # Ruta diagonal aproximada
            [
                (-38.7345, -72.5910),
                (-38.7355, -72.5920),
                (-38.7365, -72.5930),
                (-38.7375, -72.5940)
            ]
        ]
        
        self.ciclovias_reales = ejemplo_ciclovias
        self.ciclovias_cargadas = True
        
        if not MAPVIEW_AVAILABLE:
            self.actualizar_mapa()
        
        from app.utils.ui import show_snackbar
        show_snackbar("Ciclovías de ejemplo cargadas", allow_on_login=True)
    
    def recargar_ciclovias(self, instance):
        """Recarga las ciclovías desde OpenStreetMap."""
        from app.utils.ui import show_snackbar
        show_snackbar("Cargando ciclovías...", allow_on_login=True)
        self.ciclovias_reales = []
        self.ciclovias_cargadas = False
        self.cargar_ciclovias_reales()

