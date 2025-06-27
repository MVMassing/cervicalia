from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from datetime import datetime
import pandas as pd
import os
from src.infrastructure.ui.chart_generator import ChartGenerator
from src.infrastructure.ui.excel_exporter import ExcelExporter

class StatisticsScreen(Screen):
    def __init__(self, repository, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository
        self.export_dialog = None
        self.start_date_input = None
        self.end_date_input = None

    def on_enter(self):
        self.refresh_statistics()
    
    def refresh_statistics(self):
        try:
            stats = self.repository.get_statistics()
            self.ids.total_occurrences.text = f"Total de Ocorrências: {stats.total_occurrences}"
            self.ids.today_occurrences.text = f"Hoje: {stats.today_occurrences}"
            self.ids.frontal_count.text = f"Frontal: {stats.frontal_camera_count}"
            self.ids.lateral_count.text = f"Lateral: {stats.lateral_camera_count}"

            self.ids.daily_chart.texture = ChartGenerator.create_daily_occurrences_chart(stats)
            self.ids.camera_chart.texture = ChartGenerator.create_camera_distribution_chart(stats)
            self.ids.trend_chart.texture = ChartGenerator.create_weekly_trend_chart(stats)
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def go_back(self):
        self.manager.current = 'welcome'

    def open_export_dialog(self):
        content = BoxLayout(orientation='vertical', spacing='10dp', size_hint_y=None, height='120dp')
        self.start_date_input = MDTextField(hint_text="Data inicial (YYYY-MM-DD)", size_hint=(1, None), height='48dp')
        self.end_date_input = MDTextField(hint_text="Data final (YYYY-MM-DD)", size_hint=(1, None), height='48dp')
        content.add_widget(self.start_date_input)
        content.add_widget(self.end_date_input)
        self.export_dialog = MDDialog(
            title="Exportar para Excel",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Cancelar", on_press=lambda x: self.export_dialog.dismiss()),
                MDRaisedButton(text="Exportar", on_press=self.export_to_excel)
            ]
        )
        self.export_dialog.open()

    def export_to_excel(self, *args):
        start_date = self.start_date_input.text.strip()
        end_date = self.end_date_input.text.strip()
        self.export_dialog.dismiss()
        try:
            df = self._get_posture_data_df()
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
            filename = ExcelExporter.get_export_filename(start_dt, end_dt)
            filepath = ExcelExporter.export_posture_data_to_excel(df, filename, start_dt, end_dt)
            self.show_export_result(filepath)
        except Exception as e:
            self.show_export_result(None, error=str(e))

    def show_export_result(self, filepath, error=None):
        if error:
            dialog = MDDialog(title="Erro ao exportar", text=error, buttons=[MDRaisedButton(text="OK", on_press=lambda x: dialog.dismiss())])
            dialog.open()
        else:
            dialog = MDDialog(title="Exportação concluída", text=f"Arquivo salvo em:\n{filepath}", buttons=[MDRaisedButton(text="OK", on_press=lambda x: dialog.dismiss())])
            dialog.open()

    def _get_posture_data_df(self):
        import sqlite3
        conn = sqlite3.connect(self.repository.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM posture_records ORDER BY timestamp", conn)
        finally:
            conn.close()
        return df 