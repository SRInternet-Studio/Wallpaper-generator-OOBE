import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect, QUrl
from PyQt5.QtGui import QPainter, QBrush, QColor, QPalette, QFont, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.media_player = None
        self.setup_audio()
        self.animations = []
        self.init_components()
        QTimer.singleShot(100, self.start_animation_sequence)
    
    def setup_audio(self):
        try:
            self.media_player = QMediaPlayer()
            audio_files = ["bgm.mp3", "bgm.wav", "bgm.ogg", "music.mp3", "sound.mp3"]#音效名称
            audio_found = False
            
            for audio_file in audio_files:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                audio_path = os.path.join(current_dir, audio_file)
                
                if os.path.exists(audio_path):
                    media_content = QMediaContent(QUrl.fromLocalFile(audio_path))
                    self.media_player.setMedia(media_content)
                    self.media_player.setVolume(50)
                    audio_found = True
                    print(f"1 {audio_file}")
                    break
            
            if not audio_found:
                print("2")
                
        except Exception as e:
            print(f"22 {e}")
    
    def play_background_music(self):
        if self.media_player and self.media_player.media().isNull():
            print("222")
            return
        
        try:
            if self.media_player:
                self.media_player.play()
                print("11")
        except Exception as e:
            print(f"2222: {e}")
    
    def stop_background_music(self):
        try:
            if self.media_player and self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.stop()
        except Exception as e:
            print(f"22222: {e}")
    
    def init_components(self):
        screen_rect = self.rect()
        self.create_image_label(screen_rect)
        self.create_title_label(screen_rect)
        self.create_subtitle_label(screen_rect)
    
    def create_image_label(self, screen_rect):
        self.image_label = QLabel(self)
        self.image_label.setStyleSheet("background: transparent;")
        image_loaded = False
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "114514.png")
            
            print(f"tp {image_path}")
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setFixedSize(320, 320)
                    image_loaded = True
                else:
                    print("3")
            else:
                print("4")
        except Exception as e:
            print(f"5{e}")
        if not image_loaded:
            self.image_label.setText("114514.png\n未找到")
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 0, 0, 150);
                    color: white;
                    border: 2px dashed #F3F3F3;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            self.image_label.setFixedSize(320, 320)
        self.center_image()
        self.image_label.show()
        self.image_label.raise_()
    def center_image(self):
        if hasattr(self, 'image_label'):
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            parent_width = self.rect().width()
            parent_height = self.rect().height()
            center_x = (parent_width - label_width) // 2
            center_y = (parent_height - label_height) // 2
            center_y = center_y - 100
            self.image_pos = QPoint(center_x, center_y)
            self.image_label.move(self.image_pos)

    def create_title_label(self, screen_rect):
        self.title_label = QLabel("壁纸生成器 NEXT", self)
        self.title_label.setStyleSheet("""
            QLabel {
                color: rgb(243, 243, 243);
                background: transparent;
                border: none;
            }
        """)
        font = QFont()
        try:
            font.setFamily("Bahnschrift SemiCondensed")
            font.setWeight(QFont.Bold)
            font.setPointSize(58)
            self.title_label.setFont(font)
        except:
            try:
                font.setFamily("Microsoft YaHei UI")
                font.setWeight(QFont.Bold)
                font.setPointSize(48)
                self.title_label.setFont(font)
            except:
                font.setFamily("Arial")
                font.setWeight(QFont.Bold)
                font.setPointSize(48)
                self.title_label.setFont(font)
        self.title_label.adjustSize()
        self.title_start_x = (screen_rect.width() - self.title_label.width()) // 2
        self.title_start_y = (screen_rect.height() - self.title_label.height()) // 2
        self.title_label.move(self.title_start_x, self.title_start_y)
        self.title_label.setWindowOpacity(0)
        self.title_label.hide()
        
        print(f"主标题尺寸: {self.title_label.width()} x {self.title_label.height()}")
    
    def create_subtitle_label(self, screen_rect):
        self.subtitle_label = QLabel("个性化聚合图片生成平台", self)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: rgb(211, 211, 211);
                background: transparent;
                border: none;
            }
        """)
        font = QFont()
        try:
            font.setFamily("Bahnschrift SemiCondensed")
            font.setWeight(QFont.Normal)
            font.setPointSize(34)
            self.subtitle_label.setFont(font)
        except:
            try:
                font.setFamily("Microsoft YaHei UI")
                font.setWeight(QFont.Normal)
                font.setPointSize(24)
                self.subtitle_label.setFont(font)
            except:
                font.setFamily("Arial")
                font.setWeight(QFont.Normal)
                font.setPointSize(24)
                self.subtitle_label.setFont(font)
        self.subtitle_label.adjustSize()
        self.subtitle_start_x = (screen_rect.width() - self.subtitle_label.width()) // 2
        self.subtitle_start_y = screen_rect.height() + 100
        self.subtitle_label.move(self.subtitle_start_x, self.subtitle_start_y)
        self.subtitle_label.setWindowOpacity(0)
        self.subtitle_label.hide()
        print(f"副标题尺寸: {self.subtitle_label.width()} x {self.subtitle_label.height()}")
    
    def start_animation_sequence(self):
        self.window_fade_in()
        self.play_background_music()
        QTimer.singleShot(500, self.show_and_animate_texts)
        QTimer.singleShot(4000, self.window_fade_out)
    
    def window_fade_in(self):
        self.setWindowOpacity(0)
        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(800)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.start()
    
    def show_and_animate_texts(self):
        self.title_label.show()
        self.subtitle_label.show()
        self.animate_title()
        QTimer.singleShot(800, self.animate_subtitle)
    
    def animate_title(self):
        target_y = int(self.rect().height() * 0.6)
        target_x = (self.rect().width() - self.title_label.width()) // 2
        self.title_fade_anim = QPropertyAnimation(self.title_label, b"windowOpacity")
        self.title_fade_anim.setDuration(600)
        self.title_fade_anim.setStartValue(0.0)
        self.title_fade_anim.setEndValue(1.0)
        self.title_fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.title_move_anim = QPropertyAnimation(self.title_label, b"pos")
        self.title_move_anim.setDuration(1000)
        self.title_move_anim.setStartValue(QPoint(self.title_start_x, self.title_start_y))
        self.title_move_anim.setEndValue(QPoint(target_x, target_y))
        self.title_move_anim.setEasingCurve(QEasingCurve.OutBack)
        self.title_fade_anim.start()
        self.title_move_anim.start()
        QTimer.singleShot(1000, self.start_title_blinking)
    
    def start_title_blinking(self):
        self.title_label.setWindowOpacity(1.0)
        self.blink_counter = 0
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.do_single_blink)
        self.blink_timer.start(150)
    
    def do_single_blink(self):
        if self.blink_counter >= 6:
            self.blink_timer.stop()
            return
        current_opacity = self.title_label.windowOpacity()
        new_opacity = 0.0 if current_opacity > 0.5 else 1.0
        self.title_label.setWindowOpacity(new_opacity)
        
        self.blink_counter += 1
    
    def animate_subtitle(self):
        title_bottom = self.title_label.pos().y() + self.title_label.height()
        target_y = title_bottom + 50
        target_x = (self.rect().width() - self.subtitle_label.width()) // 2
        self.subtitle_fade_anim = QPropertyAnimation(self.subtitle_label, b"windowOpacity")
        self.subtitle_fade_anim.setDuration(1000)
        self.subtitle_fade_anim.setStartValue(0.0)
        self.subtitle_fade_anim.setEndValue(1.0)
        self.subtitle_fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.subtitle_move_anim = QPropertyAnimation(self.subtitle_label, b"pos")
        self.subtitle_move_anim.setDuration(1000)
        self.subtitle_move_anim.setStartValue(QPoint(self.subtitle_start_x, self.subtitle_start_y))
        self.subtitle_move_anim.setEndValue(QPoint(target_x, target_y))
        self.subtitle_move_anim.setEasingCurve(QEasingCurve.Linear)
        self.subtitle_fade_anim.start()
        self.subtitle_move_anim.start()
    
    def window_fade_out(self):
        self.stop_background_music()
        
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(800)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.finished.connect(self.close)
        self.fade_out_anim.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_image()

        if hasattr(self, 'title_label') and not self.title_label.isVisible():
            screen_rect = self.rect()
            self.title_start_x = (screen_rect.width() - self.title_label.width()) // 2
            self.title_start_y = (screen_rect.height() - self.title_label.height()) // 2
            self.title_label.move(self.title_start_x, self.title_start_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    try:
        global_font = QFont("Bahnschrift SemiCondensed")
        global_font.setWeight(QFont.Bold)
        app.setFont(global_font)
    except:
        print("使用系统默认字体")
    print("=" * 50)
    print(f"当前工作目录: {os.getcwd()}")
    print(f"目录文件列表: {os.listdir('.')}")
    print("=" * 50)
    
    window = SplashWindow()
    window.show()
    
    sys.exit(app.exec_())