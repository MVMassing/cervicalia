from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from src.infrastructure.database.sqlite_posture_repository import SQLitePostureRepository
from src.presentation.screens.welcome_screen import WelcomeScreen
from src.presentation.screens.posture_monitor_screen import PostureMonitorScreen
from src.presentation.screens.statistics_screen import StatisticsScreen

KV = '''
#:import os os

<WelcomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'

        Image:
            source: "assets/logo.png"
            size_hint: (0.5, None)
            height: "150dp"
            pos_hint: {'center_x': 0.5}
            keep_ratio: True
            allow_stretch: True
        
        MDLabel:
            text: "Bem-vindo ao Cervicalia"
            halign: 'center'
            font_style: 'H4'
            size_hint_y: None
            height: self.texture_size[1]
        
        MDRaisedButton:
            text: "Usar apenas a webcam (visão frontal)"
            size_hint: 0.8, None
            height: '50dp'
            pos_hint: {'center_x': 0.5}
            on_press: root.use_frontal_only()
        
        MDRaisedButton:
            text: "Usar WEBCAM + CELULAR (visão frontal e lateral)"
            size_hint: 0.8, None
            height: '50dp'
            pos_hint: {'center_x': 0.5}
            on_press: root.use_both_cameras()
            
        MDRaisedButton:
            text: "Ver Dados e Estatísticas"
            size_hint: 0.8, None
            height: '50dp'
            pos_hint: {'center_x': 0.5}
            on_press: root.show_statistics()

<PostureMonitorScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        
        BoxLayout:
            orientation: 'horizontal'
            spacing: '10dp'
            size_hint_y: 0.8
            
            BoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                Image:
                    id: frontal_cam
                    keep_ratio: True
                    allow_stretch: True
                
                MDLabel:
                    id: frontal_angle
                    text: "FRONTAL: Ângulos"
                    halign: 'center'
                    font_style: 'Caption'
                
                MDLabel:
                    id: frontal_status
                    text: "STATUS"
                    halign: 'center'
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1
            
            BoxLayout:
                orientation: 'vertical'
                spacing: '5dp'
                
                Image:
                    id: lateral_cam
                    keep_ratio: True
                    allow_stretch: True
                
                MDLabel:
                    id: lateral_angle
                    text: "LATERAL: Ângulos"
                    halign: 'center'
                    font_style: 'Caption'
                
                MDLabel:
                    id: lateral_status
                    text: "STATUS"
                    halign: 'center'
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.1
            spacing: '20dp'
            
            MDRaisedButton:
                text: 'Calibrar'
                on_press: root.calibrate()
                size_hint_x: 0.3
            
            MDRaisedButton:
                text: 'Voltar'
                on_press: root.go_back()
                size_hint_x: 0.3
            
            MDLabel:
                id: status
                text: "NÃO CALIBRADO"
                halign: 'center'
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                font_style: 'H6'

<StatisticsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        
        MDLabel:
            text: "Dados e Estatísticas de Postura"
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1] + 20
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: '10dp'
                size_hint_y: None
                height: self.minimum_height
                
                MDCard:
                    size_hint_y: None
                    height: '100dp'
                    padding: '10dp'
                    elevation: 2
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: '20dp'
                        
                        BoxLayout:
                            orientation: 'vertical'
                            
                            MDLabel:
                                id: total_occurrences
                                text: "Total de Ocorrências: 0"
                                font_style: 'H6'
                                size_hint_y: None
                                height: self.texture_size[1]
                                
                            MDLabel:
                                id: today_occurrences
                                text: "Hoje: 0"
                                font_style: 'Caption'
                                size_hint_y: None
                                height: self.texture_size[1]
                        
                        BoxLayout:
                            orientation: 'vertical'
                            
                            MDLabel:
                                id: frontal_count
                                text: "Frontal: 0"
                                font_style: 'Caption'
                                size_hint_y: None
                                height: self.texture_size[1]
                                
                            MDLabel:
                                id: lateral_count
                                text: "Lateral: 0"
                                font_style: 'Caption'
                                size_hint_y: None
                                height: self.texture_size[1]
                
                MDCard:
                    size_hint_y: None
                    height: '300dp'
                    padding: '10dp'
                    elevation: 2
                    
                    BoxLayout:
                        orientation: 'vertical'
                        
                        MDLabel:
                            text: "Ocorrências por Dia (Últimos 7 dias)"
                            font_style: 'Subtitle1'
                            size_hint_y: None
                            height: '30dp'
                        
                        Image:
                            id: daily_chart
                            allow_stretch: True
                            keep_ratio: True
                            size_hint: 1,1
                
                MDCard:
                    size_hint_y: None
                    height: '300dp'
                    padding: '10dp'
                    elevation: 2
                    
                    BoxLayout:
                        orientation: 'vertical'
                        
                        MDLabel:
                            text: "Distribuição por Câmera"
                            font_style: 'Subtitle1'
                            size_hint_y: None
                            height: '30dp'
                        
                        Image:
                            id: camera_chart
                            allow_stretch: True
                            keep_ratio: True
                            size_hint: 1, 1
                
                MDCard:
                    size_hint_y: None
                    height: '300dp'
                    padding: '10dp'
                    elevation: 2
                    
                    BoxLayout:
                        orientation: 'vertical'
                        
                        MDLabel:
                            text: "Tendência Semanal"
                            font_style: 'Subtitle1'
                            size_hint_y: None
                            height: '30dp'
                        
                        Image:
                            id: trend_chart
                            allow_stretch: True
                            keep_ratio: True
                            size_hint: 1, 1
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            
            MDRaisedButton:
                text: 'Atualizar Dados'
                on_press: root.refresh_statistics()
                size_hint_x: 0.33
                
            MDRaisedButton:
                text: 'Exportar para Excel'
                on_press: root.open_export_dialog()
                size_hint_x: 0.33
                
            MDRaisedButton:
                text: 'Voltar'
                on_press: root.go_back()
                size_hint_x: 0.33
'''

Builder.load_string(KV)

class CervicaliaApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        self.repository = SQLitePostureRepository()
        self.sm = ScreenManager()
        self.sm.add_widget(WelcomeScreen(self.repository, name='welcome'))
        self.sm.add_widget(PostureMonitorScreen(self.repository, name='main'))
        self.sm.add_widget(StatisticsScreen(self.repository, name='statistics'))
        
        return self.sm

    def on_stop(self):
        self.sm.get_screen('main').on_stop()
        return True

if __name__ == '__main__':
    CervicaliaApp().run()