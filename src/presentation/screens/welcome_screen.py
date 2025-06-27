from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

class WelcomeScreen(Screen):
    def __init__(self, repository, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository

    def use_frontal_only(self):
        self.manager.current = 'main'
        self.manager.get_screen('main').setup_cameras(frontal_only=True)
    
    def use_both_cameras(self):
        content = BoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height='100dp'
        )
        
        last_saved_ip = self.repository.get_setting("last_ip", "")
        
        self.ip_input = MDTextField(
            hint_text="IP Cam Access (ex: http://192.168.x.x:4747/video):",
            text=last_saved_ip,
            size_hint=(1, None),
            height='48dp'
        )
        content.add_widget(self.ip_input)
        
        self.dialog = MDDialog(
            title="Configurar Câmera Lateral",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Cancelar",
                    on_press=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Conectar",
                    on_press=self.connect_lateral_camera
                )
            ]
        )
        
        self.dialog.open()
    
    def connect_lateral_camera(self, instance):
        ip_address = self.ip_input.text.strip()
        if ip_address:
            self.repository.save_setting("last_ip", ip_address)
            self.dialog.dismiss()
            self.manager.current = 'main'
            self.manager.get_screen('main').setup_cameras(
                frontal_only=False,
                lateral_ip=ip_address
            )
    
    def show_statistics(self):
        self.manager.current = 'statistics'
        self.manager.get_screen('statistics').refresh_statistics() 