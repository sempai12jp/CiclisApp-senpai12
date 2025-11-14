from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from app.widgets.mapa_interactivo import MapaInteractivo
from app.utils.ui import show_snackbar

class PantallaMapa(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'mapa'

        # Layout principal
        self.layout = MDBoxLayout(orientation="vertical")

        # Barra superior
        self.toolbar = MDTopAppBar(
            title="Mapa de Zonas Seguras",
            elevation=0
        )
        self.layout.add_widget(self.toolbar)

        # Mapa interactivo
        self.mapa = MapaInteractivo()
        self.layout.add_widget(self.mapa)

        self.add_widget(self.layout)

    def on_enter(self):
        """Se ejecuta cuando se entra a la pantalla."""
        # Mostrar mensaje informativo
        show_snackbar("Usa el botón GPS para activar tu ubicación", duration=3.0, allow_on_login=True)
