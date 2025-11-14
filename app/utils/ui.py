from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel


def show_snackbar(mensaje: str, duration: float = 3.0, pos_hint: dict | None = None, allow_on_login: bool = False):
    """Muestra un MDSnackbar con un MDLabel interno (API segura para KivyMD).

    Parámetros:
    - mensaje: texto a mostrar
    - duration: duración en segundos
    - pos_hint: diccionario pos_hint para posicionar el snackbar (por ejemplo {'center_x':0.5, 'y':0.02})

    Uso: from app.utils.ui import show_snackbar
         show_snackbar('Hola', duration=4)
    """
    try:
        # Evitar mostrar mensajes de 'próximamente' al iniciar si la app está en la pantalla de login
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app is not None:
                try:
                    current = getattr(app.root, 'current', None)
                except Exception:
                    current = None
                if current == 'login' and 'próximamente' in (mensaje or '').lower() and not allow_on_login:
                    return
        except Exception:
            # Si no podemos consultar el app root, continuamos normalmente
            pass
        sn = MDSnackbar(duration=duration)
        if pos_hint:
            try:
                sn.pos_hint = pos_hint
            except Exception:
                # algunos contenedores podrían ignorar pos_hint; no fatal
                pass
        sn.add_widget(MDLabel(text=mensaje, halign='center'))
        sn.open()
    except Exception:
        # Fallback: intentar construir directamente con MDLabel
        try:
            MDSnackbar(MDLabel(text=mensaje)).open()
        except Exception:
            # última opción: no hacer nada
            pass

