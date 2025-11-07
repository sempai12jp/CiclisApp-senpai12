# CicloTemuco App

Estructura recomendada para un proyecto KivyMD modular y escalable.

## Estructura de carpetas

```
ProyectoApp/
│
├── main.py
├── README.md
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── pantalla_login.py
│   │   └── pantalla_principal.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   └── widget_mapa_mejorado.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── colores.py
│   │   └── rutas.py
│   └── utils/
│       └── __init__.py
│
├── assets/
│   └── icons/
│       ├── cluster.png
│       └── marker.png
│
├── kivy_venv/
└── venv/
```

- Colocar imágenes, íconos y recursos en `assets/`.
- Toda la lógica de la app va en `app/`.
- Usa `utils/` para helpers o utilidades.
- Los entornos virtuales no deben modificarse.
