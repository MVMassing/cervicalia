import matplotlib
matplotlib.use('Agg')  # Configurar backend não-interativo para executável
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from kivy.graphics.texture import Texture
from matplotlib.backends.backend_agg import FigureCanvasAgg

from ...domain.entities.statistics import PostureStatistics

class ChartGenerator:
    
    @staticmethod
    def create_daily_occurrences_chart(statistics: PostureStatistics) -> Texture:
        try:
            if not statistics.daily_occurrences:
                fig, ax = plt.subplots(figsize=(10, 6), dpi=80)
                ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=16, fontweight='bold')
                ax.set_title('Ocorrências por Dia (Últimos 7 dias)', fontsize=18, pad=20)
                plt.tight_layout()
                return ChartGenerator._fig_to_texture(fig)
            
            today = datetime.now().date()
            week_ago = today - timedelta(days=6)
            
            date_range = pd.date_range(start=week_ago, end=today, freq='D')
            daily_counts = []
            
            for date in date_range:
                date_str = date.date().isoformat()
                daily_counts.append(statistics.daily_occurrences.get(date_str, 0))
            
            fig, ax = plt.subplots(figsize=(10, 6), dpi=80)
            fig.patch.set_facecolor('white')
            
            bars = ax.bar(range(len(daily_counts)), daily_counts, 
                         color='#3498db', alpha=0.8, edgecolor='#2980b9', linewidth=1)
            
            ax.set_xlabel('Data', fontsize=14, fontweight='bold')
            ax.set_ylabel('Número de Ocorrências', fontsize=14, fontweight='bold')
            ax.set_title('Ocorrências por Dia (Últimos 7 dias)', fontsize=18, pad=20, fontweight='bold')
            ax.set_xticks(range(len(daily_counts)))
            ax.set_xticklabels([d.strftime('%d/%m') for d in date_range], 
                              rotation=45, ha='right', fontsize=12)
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_ylim(0, max(daily_counts) * 1.2 if max(daily_counts) > 0 else 1)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='both', which='major', labelsize=11)
            
            plt.tight_layout()
            return ChartGenerator._fig_to_texture(fig)
        except Exception as e:
            print(f"Erro ao criar gráfico diário: {e}")
            return ChartGenerator._create_error_texture("Erro ao gerar gráfico")
    
    @staticmethod
    def create_camera_distribution_chart(statistics: PostureStatistics) -> Texture:
        try:
            if not statistics.camera_distribution:
                fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
                fig.patch.set_facecolor('white')
                ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=16, fontweight='bold')
                ax.set_title('Distribuição por Câmera', fontsize=18)
                return ChartGenerator._fig_to_texture(fig)
            
            camera_counts = statistics.camera_distribution
            
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.patch.set_facecolor('white')
            colors = ['#e74c3c', '#3498db']
            
            wedges, texts, autotexts = ax.pie(camera_counts.values(), 
                                             labels=[f'Câmera {label.title()}' for label in camera_counts.keys()],
                                             autopct='%1.1f%%',
                                             colors=colors[:len(camera_counts)],
                                             startangle=90,
                                             textprops={'fontsize': 14, 'fontweight': 'bold'})
            
            ax.set_title('Distribuição de Ocorrências por Câmera', fontsize=18, pad=20, fontweight='bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(14)
            
            legend_labels = [f'{label.title()}: {count}' for label, count in camera_counts.items()]
            ax.legend(wedges, legend_labels, title="Totais", loc="center left", 
                     bbox_to_anchor=(1, 0, 0.5, 1), fontsize=12)
            
            plt.tight_layout()
            return ChartGenerator._fig_to_texture(fig)
        except Exception as e:
            print(f"Erro ao criar gráfico de distribuição: {e}")
            return ChartGenerator._create_error_texture("Erro ao gerar gráfico")
    
    @staticmethod
    def create_weekly_trend_chart(statistics: PostureStatistics) -> Texture:
        try:
            if not statistics.weekly_trend:
                fig, ax = plt.subplots(figsize=(10, 6), dpi=80)
                fig.patch.set_facecolor('white')
                ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=14)
                ax.set_title('Tendência Semanal', fontsize=16)
                plt.tight_layout()
                return ChartGenerator._fig_to_texture(fig)
            
            weekly_counts = statistics.weekly_trend
            
            if len(weekly_counts) < 2:
                fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
                ax.text(0.5, 0.5, 'Dados insuficientes para tendência\n(mínimo 2 semanas)', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title('Tendência Semanal', fontsize=16)
                plt.tight_layout()
                return ChartGenerator._fig_to_texture(fig)
            
            fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
            
            x_values = range(len(weekly_counts))
            y_values = list(weekly_counts.values())
            
            ax.plot(x_values, y_values, marker='o', linewidth=3, markersize=8, 
                   color='#e74c3c', markerfacecolor='#c0392b', markeredgecolor='white', 
                   markeredgewidth=2)
            
            ax.set_xlabel('Semana', fontsize=12)
            ax.set_ylabel('Número de Ocorrências', fontsize=12)
            ax.set_title('Tendência Semanal de Ocorrências', fontsize=16, pad=20)
            ax.set_xticks(x_values)
            
            week_labels = [f'S{i+1}' for i in range(len(weekly_counts))]
            ax.set_xticklabels(week_labels, rotation=0)
            
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, max(y_values) * 1.2 if max(y_values) > 0 else 1)
            
            for i, value in enumerate(y_values):
                ax.annotate(f'{value}', (i, value), textcoords="offset points", 
                           xytext=(0,15), ha='center', fontsize=10, 
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            if len(y_values) >= 2:
                first_week = y_values[0]
                last_week = y_values[-1]
                
                if first_week > 0:
                    change_percent = ((last_week - first_week) / first_week) * 100
                    trend_text = f"Mudança: {change_percent:+.1f}%"
                    color = '#27ae60' if change_percent < 0 else '#e74c3c'
                    
                    ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, 
                           verticalalignment='top', fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.2))
            
            plt.tight_layout()
            return ChartGenerator._fig_to_texture(fig)
        except Exception as e:
            print(f"Erro ao criar gráfico de tendência: {e}")
            return ChartGenerator._create_error_texture("Erro ao gerar gráfico")
    
    @staticmethod
    def _fig_to_texture(fig) -> Texture:
        try:
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            texture = Texture.create(size=size, colorfmt='rgb')
            texture.blit_buffer(raw_data, colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            
            plt.close(fig)
            return texture
        except Exception as e:
            print(f"Erro ao converter figura para textura: {e}")
            return ChartGenerator._create_error_texture("Erro de renderização")
    
    @staticmethod
    def _create_error_texture(message: str) -> Texture:
        """Cria uma textura com mensagem de erro"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.patch.set_facecolor('white')
            ax.text(0.5, 0.5, message, ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, fontweight='bold', color='red')
            ax.set_title('Erro', fontsize=16, color='red')
            plt.tight_layout()
            return ChartGenerator._fig_to_texture(fig)
        except:
            from kivy.core.image import Image as CoreImage
            import io
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (400, 300), color='white')
                draw = ImageDraw.Draw(img)
                draw.text((200, 150), message, fill='red', anchor='mm')               
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                
                core_image = CoreImage(io.BytesIO(buffer.getvalue()), ext='png')
                return core_image.texture
            except:
                return Texture.create(size=(400, 300), colorfmt='rgb') 