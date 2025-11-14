from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.textfield import MDTextField
from app.utils.ui import show_snackbar
from kivy.metrics import dp
import os
import json
import csv

class ListaReportes(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'lista_reportes'
        from kivymd.uix.toolbar import MDTopAppBar
        layout = MDBoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        self.toolbar = MDTopAppBar(title='Reportes guardados', left_action_items=[['arrow-left', lambda x: self.volver_principal(x)]])
        layout.add_widget(self.toolbar)

        # Filtros y acciones
        filtros_row = MDBoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        self.filter_tipo = MDTextField(hint_text='Filtrar por tipo', size_hint_x=0.5)
        self.filter_fecha = MDTextField(hint_text='Filtrar por fecha (YYYY-MM-DD)', size_hint_x=0.5)
        filtros_row.add_widget(self.filter_tipo)
        filtros_row.add_widget(self.filter_fecha)
        layout.add_widget(filtros_row)

        acciones_row = MDBoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        btn_filtrar = MDRaisedButton(text='Aplicar filtro', on_release=self.aplicar_filtro)
        btn_export = MDRaisedButton(text='Exportar CSV', on_release=self.exportar_csv)
        btn_borrar = MDRaisedButton(text='Borrar todos', on_release=self.confirmar_borrar_todos)
        acciones_row.add_widget(btn_filtrar)
        acciones_row.add_widget(btn_export)
        acciones_row.add_widget(btn_borrar)
        layout.add_widget(acciones_row)

        self.scroll = MDScrollView()
        self.md_list = MDList()
        self.scroll.add_widget(self.md_list)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
        self.load_reportes()

    def volver_principal(self, instance):
        if self.manager:
            self.manager.current = 'principal'

    def load_reportes(self):
        app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(app_root, 'reportes_peligro.json')
        self.md_list.clear_widgets()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tipo_filtro = (self.filter_tipo.text.strip().lower() if hasattr(self, 'filter_tipo') else '')
                fecha_filtro = (self.filter_fecha.text.strip() if hasattr(self, 'filter_fecha') else '')
                for rpt in data:
                    # aplicar filtros
                    if tipo_filtro and tipo_filtro not in rpt.get('tipo', '').lower():
                        continue
                    if fecha_filtro and fecha_filtro not in rpt.get('fecha', ''):
                        continue
                    fecha = rpt.get('fecha', '')
                    calle = rpt.get('calle', '---')
                    tipo = rpt.get('tipo', '---')
                    texto = f"{calle} — {tipo} ({fecha.split('T')[0] if fecha else ''})"
                    item = OneLineListItem(text=texto, on_release=lambda x, r=rpt: self.mostrar_detalle(r))
                    self.md_list.add_widget(item)
            except Exception:
                self.md_list.add_widget(OneLineListItem(text='No se pudieron cargar los reportes'))
        else:
            self.md_list.add_widget(OneLineListItem(text='No hay reportes guardados'))

    def mostrar_detalle(self, reporte):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        texto = f"Calle: {reporte.get('calle')}\nTipo: {reporte.get('tipo')}\nDescripción: {reporte.get('descripcion')}\nFecha: {reporte.get('fecha')}"
        def _close(obj):
            dialog.dismiss()

        def _elim(obj):
            dialog.dismiss()
            self.eliminar_reporte(reporte)

        dialog = MDDialog(title='Detalle del reporte', text=texto, buttons=[MDFlatButton(text='Cerrar', on_release=_close), MDRaisedButton(text='Eliminar', on_release=_elim)])
        dialog.open()

    def eliminar_reporte(self, reporte):
        app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(app_root, 'reportes_peligro.json')
        if not os.path.exists(file_path):
            show_snackbar('No hay archivo de reportes')
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # eliminar por coincidencia de objeto (fecha única)
            nueva = [r for r in data if r.get('fecha') != reporte.get('fecha')]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(nueva, f, indent=2, ensure_ascii=False)
            show_snackbar('Reporte eliminado')
            self.load_reportes()
        except Exception as e:
            show_snackbar(f'Error eliminando reporte: {e}')

    def aplicar_filtro(self, instance):
        self.load_reportes()

    def exportar_csv(self, instance):
        app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(app_root, 'reportes_peligro.json')
        csv_path = os.path.join(app_root, 'reportes_peligro.csv')
        if not os.path.exists(file_path):
            show_snackbar('No hay reportes para exportar')
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['calle', 'tipo', 'descripcion', 'fecha'])
                for r in data:
                    writer.writerow([r.get('calle'), r.get('tipo'), r.get('descripcion'), r.get('fecha')])
            show_snackbar(f'Exportado a {csv_path}')
        except Exception as e:
            show_snackbar(f'Error exportando CSV: {e}')

    def confirmar_borrar_todos(self, instance):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        def _cancel(obj):
            dlg.dismiss()
        def _confirm(obj):
            dlg.dismiss()
            self.borrar_todos()
        dlg = MDDialog(title='Confirmar', text='¿Borrar todos los reportes?', buttons=[MDFlatButton(text='Cancelar', on_release=_cancel), MDRaisedButton(text='Borrar', on_release=_confirm)])
        dlg.open()

    def borrar_todos(self):
        app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(app_root, 'reportes_peligro.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            show_snackbar('Todos los reportes han sido borrados')
            self.load_reportes()
        except Exception as e:
            show_snackbar(f'Error borrando reportes: {e}')
