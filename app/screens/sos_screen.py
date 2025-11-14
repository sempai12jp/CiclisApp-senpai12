from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from plyer import gps
import requests
from app.utils.ui import show_snackbar

class WeatherScreen(MDScreen):
    """Pantalla de clima mejorada para ciclistas con GPS y diseño moderno."""

    API_KEY = "e93a5bdb07a04dca86d908749275ce5b"  # API key de OpenWeatherMap

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'weather'
        self.ubicacion_gps = None
        self.gps_enabled = False
        
        # Layout principal con scroll
        scroll = MDScrollView()
        layout = MDBoxLayout(orientation='vertical', padding=[dp(16), dp(20), dp(16), dp(20)], spacing=dp(24), 
                           size_hint_y=None, adaptive_height=True)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Card principal del clima - Diseño similar al wireframe
        self.weather_card = MDCard(
            orientation='vertical',
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(16),
            radius=[20, 20, 20, 20],
            elevation=4,
            size_hint=(1, None),
            adaptive_height=True,
            md_bg_color=(0.95, 0.97, 1.0, 1)
        )
        
        # Título "Clima Actual"
        title_label = MDLabel(
            text='Clima Actual',
            font_style='H5',
            theme_text_color='Primary',
            halign='left',
            size_hint_y=None,
            height=dp(40)
        )
        self.weather_card.add_widget(title_label)
        
        # Contenedor principal: ícono a la izquierda, temperatura a la derecha
        main_content = MDBoxLayout(orientation='horizontal', spacing=dp(20), 
                                   size_hint_y=None, height=dp(180),
                                   padding=[dp(0), dp(10), dp(0), dp(10)])
        
        # Ícono del clima grande (lado izquierdo)
        icon_container = MDBoxLayout(orientation='vertical', size_hint_x=0.4)
        self.weather_image = AsyncImage(
            source='',
            size_hint=(None, None),
            size=(dp(140), dp(140)),
            allow_stretch=True,
            keep_ratio=True
        )
        # Centrar el ícono
        icon_box = MDBoxLayout(orientation='vertical', size_hint=(1, 1))
        icon_box.add_widget(MDLabel(size_hint_y=None, height=dp(20)))
        icon_box.add_widget(self.weather_image)
        icon_box.add_widget(MDLabel(size_hint_y=None, height=dp(20)))
        icon_container.add_widget(icon_box)
        main_content.add_widget(icon_container)
        
        # Temperatura y descripción (lado derecho)
        temp_container = MDBoxLayout(orientation='vertical', size_hint_x=0.6, spacing=dp(8))
        
        # Espaciador para alinear con el ícono
        temp_container.add_widget(MDLabel(size_hint_y=None, height=dp(20)))
        
        # Temperatura grande
        temp_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), spacing=dp(4))
        self.temp_number_label = MDLabel(
            text='--',
            font_style='H1',
            halign='left',
            theme_text_color='Primary',
            size_hint_x=0.75
        )
        temp_row.add_widget(self.temp_number_label)
        
        self.temp_unit_label = MDLabel(
            text='°C',
            font_size=dp(50),
            halign='left',
            theme_text_color='Primary',
            size_hint_x=0.25
        )
        temp_row.add_widget(self.temp_unit_label)
        temp_container.add_widget(temp_row)
        
        # Descripción del clima debajo de la temperatura
        self.desc_label = MDLabel(
            text='Cargando datos...',
            font_style='H6',
            halign='left',
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(40)
        )
        temp_container.add_widget(self.desc_label)
        
        main_content.add_widget(temp_container)
        self.weather_card.add_widget(main_content)
        
        # Indicador de ubicación (oculto por defecto, se muestra cuando hay GPS)
        self.location_label = MDLabel(
            text='',
            font_style='Body2',
            theme_text_color='Secondary',
            halign='center',
            size_hint_y=None,
            height=dp(0),
            opacity=0
        )
        self.weather_card.add_widget(self.location_label)
        
        # Card de detalles - Diseño con mejor espaciado
        self.details_card = MDCard(
            orientation='vertical',
            padding=[dp(24), dp(24), dp(24), dp(24)],
            spacing=dp(16),
            radius=[20, 20, 20, 20],
            elevation=4,
            size_hint=(1, None),
            adaptive_height=True,
            md_bg_color=(1, 1, 1, 1)
        )
        
        # Título "Detalles del clima"
        details_title = MDLabel(
            text='Detalles del clima',
            font_style='H6',
            theme_text_color='Primary',
            halign='left',
            size_hint_y=None,
            height=dp(40)
        )
        self.details_card.add_widget(details_title)
        
        # Espaciador después del título
        self.details_card.add_widget(MDLabel(size_hint_y=None, height=dp(12)))
        
        # Detalles con mejor espaciado: Viento y Humedad
        self.details_container = MDBoxLayout(orientation='vertical', spacing=dp(20))
        
        # Viento
        wind_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        wind_row.add_widget(MDLabel(
            text='Viento:',
            font_style='Body1',
            halign='left',
            theme_text_color='Secondary',
            size_hint_x=0.4
        ))
        self.wind_label = MDLabel(
            text='-- km/h',
            font_style='Body1',
            halign='left',
            theme_text_color='Primary',
            size_hint_x=0.6
        )
        wind_row.add_widget(self.wind_label)
        self.details_container.add_widget(wind_row)
        
        # Humedad
        humidity_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        humidity_row.add_widget(MDLabel(
            text='Humedad:',
            font_style='Body1',
            halign='left',
            theme_text_color='Secondary',
            size_hint_x=0.4
        ))
        self.humidity_label = MDLabel(
            text='--%',
            font_style='Body1',
            halign='left',
            theme_text_color='Primary',
            size_hint_x=0.6
        )
        humidity_row.add_widget(self.humidity_label)
        self.details_container.add_widget(humidity_row)
        
        self.details_card.add_widget(self.details_container)
        
        # Botones de acción - Diseño similar al wireframe
        buttons_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(56), padding=[dp(0), dp(8), dp(0), dp(0)])
        
        self.btn_actualizar = MDRaisedButton(
            text='Actualizar',
            size_hint=(1, 1),
            md_bg_color=(0.2, 0.6, 0.9, 1),
            on_release=self.update_weather
        )
        buttons_layout.add_widget(self.btn_actualizar)
        
        self.btn_ubicacion = MDRaisedButton(
            text='Mi ubicacion',
            size_hint=(1, 1),
            md_bg_color=(0.1, 0.8, 0.3, 1),
            on_release=self.usar_ubicacion_gps
        )
        buttons_layout.add_widget(self.btn_ubicacion)
        
        # Agregar cards al layout en orden
        layout.add_widget(self.weather_card)
        
        # Espaciador entre cards principales
        layout.add_widget(MDLabel(size_hint_y=None, height=dp(8)))
        
        # Card de detalles separado abajo
        layout.add_widget(self.details_card)
        
        # Espaciador antes de los botones
        layout.add_widget(MDLabel(size_hint_y=None, height=dp(8)))
        
        # Botones al final
        layout.add_widget(buttons_layout)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        
        # Configurar GPS
        self.configurar_gps()
        
        # Actualizar clima al iniciar
        Clock.schedule_once(lambda dt: self.update_weather(), 1)
    
    def configurar_gps(self):
        """Configura el GPS para obtener ubicación automática."""
        try:
            gps.configure(on_location=self.on_gps_location)
        except Exception as e:
            print(f"GPS no disponible: {e}")
    
    def on_gps_location(self, **kwargs):
        """Callback cuando se recibe una ubicación GPS."""
        try:
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            if lat and lon:
                self.ubicacion_gps = (lat, lon)
                # Actualizar clima automáticamente cuando cambia la ubicación
                self.update_weather_by_coords(lat, lon)
        except Exception as e:
            print(f"Error procesando ubicación GPS: {e}")
    
    def toggle_gps(self, instance):
        """Activa o desactiva el GPS."""
        try:
            if not self.gps_enabled:
                try:
                    gps.start(minTime=5000, minDistance=100)
                    self.gps_enabled = True
                    self.btn_gps.icon_color = (0.2, 0.9, 0.2, 1)  # Verde cuando está activo
                    show_snackbar("GPS activado", allow_on_login=True)
                except Exception as e:
                    # En Windows/desarrollo, simular ubicación
                    print(f"GPS no disponible, usando ubicación simulada: {e}")
                    self.ubicacion_gps = (-38.7359, -72.5904)  # Temuco
                    self.gps_enabled = True
                    self.btn_gps.icon_color = (0.8, 0.8, 0.2, 1)  # Amarillo para simulado
                    show_snackbar("GPS simulado (Temuco)", allow_on_login=True)
                    self.update_weather_by_coords(*self.ubicacion_gps)
            else:
                try:
                    gps.stop()
                except:
                    pass
                self.gps_enabled = False
                self.btn_gps.icon_color = (0.2, 0.6, 0.9, 1)  # Azul cuando está inactivo
                show_snackbar("GPS desactivado", allow_on_login=True)
        except Exception as e:
            print(f"Error al activar GPS: {e}")
            show_snackbar(f"Error GPS: {str(e)}", allow_on_login=True)
    
    def usar_ubicacion_gps(self, instance):
        """Usa la ubicación GPS para obtener el clima."""
        if self.ubicacion_gps:
            self.update_weather_by_coords(*self.ubicacion_gps)
        else:
            show_snackbar("Activa el GPS primero", allow_on_login=True)
            self.toggle_gps(None)
    
    def update_weather(self, dt=None):
        """Actualiza el clima usando la ubicación GPS si está disponible, sino usa Temuco."""
        if self.ubicacion_gps:
            self.update_weather_by_coords(*self.ubicacion_gps)
        else:
            # Usar Temuco por defecto
            self.update_weather_by_coords(-38.7359, -72.5904)
    
    def update_weather_by_coords(self, lat, lon):
        """Actualiza el clima usando coordenadas GPS."""
        try:
            # Usar API de OpenWeatherMap con coordenadas (más preciso)
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.API_KEY}&units=metric&lang=es"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                city_name = data.get('name', 'Ubicación actual')
                temp = round(data['main']['temp'])
                feels_like = round(data['main']['feels_like'])
                humidity = data['main']['humidity']
                wind_speed = round(data.get('wind', {}).get('speed', 0) * 3.6)  # Convertir m/s a km/h
                desc = data['weather'][0]['description'].capitalize()
                icon_code = data['weather'][0]['icon']
                
                # Actualizar UI
                # Mostrar ubicación si hay GPS activo
                if self.gps_enabled and self.ubicacion_gps:
                    self.location_label.text = f'📍 {city_name}'
                    self.location_label.height = dp(30)
                    self.location_label.opacity = 1
                else:
                    self.location_label.text = ''
                    self.location_label.height = dp(0)
                    self.location_label.opacity = 0
                
                self.temp_number_label.text = f'{temp}'
                self.desc_label.text = desc.capitalize()
                
                # Actualizar imagen del clima usando URL de OpenWeatherMap
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                self.weather_image.source = icon_url
                
                # Actualizar detalles
                self.humidity_label.text = f'{humidity}%'
                self.wind_label.text = f'{wind_speed} km/h'
                
                # Cambiar color del card según el clima
                self.actualizar_color_card(icon_code, temp)
                
                show_snackbar('🌦️ Clima actualizado', allow_on_login=True)
                
            elif response.status_code == 401:
                self.mostrar_error_api()
            else:
                error_msg = data.get('message', 'Error desconocido')
                show_snackbar(f'Error: {error_msg}', allow_on_login=True)
                self.mostrar_datos_ejemplo()
                
        except requests.exceptions.Timeout:
            show_snackbar('⏱️ Tiempo de espera agotado', allow_on_login=True)
            self.mostrar_datos_ejemplo()
        except requests.exceptions.RequestException as e:
            show_snackbar(f'❌ Error de conexión: {str(e)}', allow_on_login=True)
            self.mostrar_datos_ejemplo()
        except Exception as e:
            show_snackbar(f'Error: {str(e)}', allow_on_login=True)
            self.mostrar_datos_ejemplo()
    
    def actualizar_color_card(self, icon_code, temp):
        """Actualiza el color del card según el clima."""
        # Colores según el tipo de clima
        if '01' in icon_code:  # Despejado
            color = (1.0, 0.95, 0.7, 1)  # Amarillo claro
        elif '02' in icon_code or '03' in icon_code or '04' in icon_code:  # Nublado
            color = (0.9, 0.9, 0.95, 1)  # Gris claro
        elif '09' in icon_code or '10' in icon_code:  # Lluvia
            color = (0.7, 0.85, 1.0, 1)  # Azul claro
        elif '11' in icon_code:  # Tormenta
            color = (0.6, 0.7, 0.9, 1)  # Azul oscuro
        elif '13' in icon_code:  # Nieve
            color = (0.95, 0.95, 1.0, 1)  # Blanco azulado
        else:
            color = (0.95, 0.97, 1.0, 1)  # Por defecto
        
        self.weather_card.md_bg_color = color
    
    def mostrar_error_api(self):
        """Muestra un mensaje de error de API."""
        self.location_label.text = '📍 Error de API'
        self.temp_number_label.text = '--'
        self.desc_label.text = 'API key inválida'
        self.weather_image.source = ''  # Limpiar imagen
        if hasattr(self, 'humidity_label'):
            self.humidity_label.text = '--%'
        if hasattr(self, 'wind_label'):
            self.wind_label.text = '-- km/h'
        self.weather_card.md_bg_color = (1.0, 0.9, 0.9, 1)  # Rojo claro
        show_snackbar('⚠️ API key inválida. Verifica tu API key de OpenWeatherMap', allow_on_login=True)
    
    def mostrar_datos_ejemplo(self):
        """Muestra datos de ejemplo cuando hay error."""
        self.location_label.text = '📍 Temuco (Ejemplo)'
        self.temp_number_label.text = '18'
        self.desc_label.text = 'Parcialmente nublado'
        # Usar ícono de ejemplo para parcialmente nublado
        self.weather_image.source = "http://openweathermap.org/img/wn/02d@2x.png"
        if hasattr(self, 'humidity_label'):
            self.humidity_label.text = '65%'
        if hasattr(self, 'wind_label'):
            self.wind_label.text = '15 km/h'
        self.weather_card.md_bg_color = (0.9, 0.9, 0.95, 1)
    
    
    def on_leave(self):
        """Se ejecuta cuando se sale de la pantalla."""
        # Detener GPS si está activo
        if self.gps_enabled:
            try:
                gps.stop()
                self.gps_enabled = False
            except:
                pass
