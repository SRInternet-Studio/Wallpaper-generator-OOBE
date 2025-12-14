import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QLabel, QPushButton, QStackedWidget, QComboBox,
                              QCheckBox, QHBoxLayout, QFileDialog, QLineEdit, QSizePolicy, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, QPropertyAnimation, QTimer, QPoint,
                           QParallelAnimationGroup, QEasingCurve, QSize, QRect,
                           Signal, QPointF, QObject)
from PySide6.QtGui import (QPixmap, QFont, QPalette,
                          QColor, QPainter, QImage, QMouseEvent)
from threading import Thread, Event
import time

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("警告: OpenCV未安装，将无法播放视频")


class VideoPlayer(QObject):
    """
    负责在后台线程用 OpenCV 读取视频帧，并把当前帧放到 self.current_frame（QImage）中。
    使用 frame_ready Event 标记主线程可以读取 current_frame。
    新增 video_finished_signal 在视频播放结束时通知主线程。
    """
    video_finished_signal = Signal()

    def __init__(self, video_path, parent_window):
        super().__init__()
        self.video_path = video_path
        self.parent_window = parent_window  # 只用于回调 video_finished()
        self.cap = None
        self.is_playing = False
        self.current_frame = None
        self.video_width = 0
        self.video_height = 0
        self.frame_ready = Event()
        self.fps = 30
        self.thread = None

    def play(self):
        if not OPENCV_AVAILABLE:
            print("OpenCV不可用，跳过视频播放")
            QTimer.singleShot(0, self.parent_window.video_finished)
            return

        def run_video():
            try:
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    print("无法打开视频文件:", self.video_path)
                    QTimer.singleShot(0, self.parent_window.video_finished)
                    return

                self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                try:
                    self.fps = float(fps) if fps and fps > 0 else 30.0
                except Exception:
                    self.fps = 30.0

                self.is_playing = True

                while self.is_playing:
                    ret, frame = self.cap.read()
                    if not ret:
                        break

                    try:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_frame.shape
                        bytes_per_line = ch * w
                        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                        self.current_frame = qimg
                        self.frame_ready.set()
                    except Exception as e:
                        print("帧转换错误:", e)
                        pass

                    time.sleep(1.0 / self.fps)

                self.is_playing = False
                # 改成发信号通知
                self.video_finished_signal.emit()

            except Exception as e:
                print(f"视频播放线程错误: {e}")
                self.video_finished_signal.emit()
            finally:
                if self.cap:
                    self.cap.release()

        self.thread = Thread(target=run_video, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_playing = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        self.frame_ready.clear()
        self.current_frame = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)


class MainWindow(QMainWindow):
    settings_updated = Signal(dict)

    def __init__(self):
        super().__init__()

        self.settings = {
            "theme_config": "Auto",
            "download_path": os.path.abspath('./Images'),
            "today_image_config": True,
            "trayicon_config": True
        }

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Main Window")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

    def setup_connections(self):
        self.settings_updated.connect(self.update_window_style)

    def update_window_style(self, settings):
        theme = settings.get("theme_config", "Auto")

        if theme == "Dark":
            self.set_dark_theme()
        elif theme == "Light":
            self.set_light_theme()
        else:
            if self.palette().window().color().lightness() < 128:
                self.set_dark_theme()
            else:
                self.set_light_theme()

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

    def set_light_theme(self):
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, Qt.white)
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, Qt.white)
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, Qt.white)
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(0, 0, 255))
        light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(light_palette)


class OOBEWindow(QMainWindow):
    settings_updated = Signal(dict)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.video_player = None
        self.video_update_timer = None  # QTimer 用来在主线程检测并刷新帧
        self.drag_pos = QPointF()

        self.settings = {
            "theme_config": "Auto",
            "download_path": os.path.abspath('./Images'),
            "today_image_config": True,
            "trayicon_config": True
        }

        self.setup_ui()
        self.setup_animations()

        self.show_window()
        self.play_intro_video()

    def closeEvent(self, event):
        # 停掉视频定时器并停止播放线程（如有）
        if self.video_update_timer and self.video_update_timer.isActive():
            self.video_update_timer.stop()
        if self.video_player:
            self.video_player.stop()

        if self.parent:
            self.parent.settings = self.settings
            self.parent.update_window_style(self.settings)
        super().closeEvent(event)

    def setup_ui(self):
        self.setWindowTitle("欢迎使用")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1070, 650)

        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            #mainWidget {
                background-color: transparent;
                border-radius: 12px;
            }
        """)

        self.stacked_widget = QStackedWidget()

        # 用于放视频的占位 widget（我们在整个窗体 paintEvent 中绘制视频）
        self.video_container = QWidget()
        self.video_container.setStyleSheet("background: transparent;")

        # 欢迎页面（设置界面）
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setContentsMargins(40, 40, 40, 40)
        welcome_layout.setSpacing(30)

        self.title_label = AnimatedLabel("欢迎使用")
        self.title_label.setFont(QFont("Arial", 28, QFont.Bold))

        self.desc_label = AnimatedLabel("感谢您选择我们的产品")
        self.desc_label.setFont(QFont("Arial", 16))

        self.setup_settings_ui()

        self.start_button = QPushButton("进入应用")
        self.start_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.start_button.setFixedSize(180, 50)
        self.start_button.clicked.connect(self.close)

        welcome_layout.addStretch()
        welcome_layout.addWidget(self.title_label)
        welcome_layout.addWidget(self.desc_label)
        welcome_layout.addStretch()
        welcome_layout.addLayout(self.settings_layout)
        welcome_layout.addStretch()
        welcome_layout.addWidget(self.start_button, 0, Qt.AlignCenter)
        welcome_layout.addStretch()

        self.welcome_page.setLayout(welcome_layout)

        self.stacked_widget.addWidget(self.video_container)  # index 0 -> 视频
        self.stacked_widget.addWidget(self.welcome_page)    # index 1 -> 设置

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)

        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)

    def setup_settings_ui(self):
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setSpacing(20)

        top_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        if os.path.exists("114514.png"):
            pixmap = QPixmap("114514.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        top_layout.addWidget(icon_label, 0, Qt.AlignLeft | Qt.AlignTop)

        right_layout = QVBoxLayout()

        theme_layout = QHBoxLayout()
        theme_label = QLabel("应用主题:")
        theme_label.setFont(QFont("Arial", 12))
        theme_label.setFixedWidth(180)
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(QFont("Arial", 12))
        self.theme_combo.addItems(["Auto", "Light", "Dark"])
        self.theme_combo.setCurrentText(self.settings["theme_config"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        download_layout = QHBoxLayout()
        download_label = QLabel("图片保存目录:")
        download_label.setFont(QFont("Arial", 12))
        download_label.setFixedWidth(180)
        self.download_path_edit = QLineEdit(self.settings["download_path"])
        self.download_path_edit.setFont(QFont("Arial", 12))
        self.download_path_edit.setReadOnly(True)
        browse_button = QPushButton("浏览...")
        browse_button.setFont(QFont("Arial", 12))
        browse_button.setFixedSize(100, 30)
        browse_button.clicked.connect(self.browse_download_path)
        download_layout.addWidget(download_label)
        download_layout.addWidget(self.download_path_edit)
        download_layout.addWidget(browse_button)

        today_image_check = QCheckBox("启用每日一图")
        today_image_check.setFont(QFont("Arial", 12))
        today_image_check.setChecked(self.settings["today_image_config"])
        today_image_check.stateChanged.connect(
            lambda state: self.on_setting_changed("today_image_config", state == Qt.Checked)
        )

        trayicon_check = QCheckBox("关闭最小化到托盘(不关闭壁纸生成器)")
        trayicon_check.setFont(QFont("Arial", 12))
        trayicon_check.setChecked(self.settings["trayicon_config"])
        trayicon_check.stateChanged.connect(
            lambda state: self.on_setting_changed("trayicon_config", state == Qt.Checked)
        )

        right_layout.addLayout(theme_layout)
        right_layout.addLayout(download_layout)
        right_layout.addWidget(today_image_check)
        right_layout.addWidget(trayicon_check)

        top_layout.addLayout(right_layout)
        self.settings_layout.addLayout(top_layout)

    def on_theme_changed(self, theme):
        self.settings["theme_config"] = theme
        self.settings_updated.emit(self.settings)

    def on_setting_changed(self, key, value):
        self.settings[key] = value

    def browse_download_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择图片保存目录",
            self.settings["download_path"]
        )
        if path:
            self.settings["download_path"] = path
            self.download_path_edit.setText(path)

    def setup_animations(self):
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(500)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)

        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(800)
        self.pos_animation.setEasingCurve(QEasingCurve.OutBack)

        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.addAnimation(self.pos_animation)

    def play_intro_video(self):
        video_path = "114514.mp4"
        if not OPENCV_AVAILABLE:
            print("OpenCV 不可用，跳过视频并显示欢迎页")
            self.video_finished()
            return

        if not os.path.exists(video_path):
            print(f"视频文件 {video_path} 不存在，直接进入欢迎页")
            self.video_finished()
            return

        self.video_player = VideoPlayer(video_path, self)
        self.video_player.video_finished_signal.connect(self.video_finished)
        self.video_player.play()

        if self.video_update_timer is None:
            self.video_update_timer = QTimer(self)
            self.video_update_timer.timeout.connect(self._on_check_frame)
        self.video_update_timer.start(30)

        self.stacked_widget.setCurrentWidget(self.video_container)

    def _on_check_frame(self):
        if not self.video_player:
            return

        if self.video_player.frame_ready.is_set():
            self.update()
            self.video_player.frame_ready.clear()

    def show_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.center().x() - self.width() // 2
        y = screen_geometry.center().y() - self.height() // 2

        start_pos = QPoint(x, y + 50)
        end_pos = QPoint(x, y)

        self.pos_animation.setStartValue(start_pos)
        self.pos_animation.setEndValue(end_pos)

        self.show()
        self.raise_()
        self.activateWindow()
        self.animation_group.start()

    def video_finished(self):
        print("视频播放结束，切换界面")
        if self.video_update_timer and self.video_update_timer.isActive():
            self.video_update_timer.stop()
        if self.video_player:
            self.video_player.stop()

        palette = self.palette()
        bg_color = palette.window().color()
        text_color = palette.windowText().color()

        self.main_widget.setStyleSheet(f"""
            #mainWidget {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 0.95);
                border-radius: 12px;
                border: 1px solid rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 0.1);
            }}
        """)

        self.title_label.setStyleSheet(f"color: {text_color.name()}; padding: 5px;")
        self.desc_label.setStyleSheet(f"color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 0.8); padding: 5px;")

        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #B498E6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #A288D6; }
            QPushButton:pressed { background-color: #8F78C2; }
        """)

        self.stacked_widget.setCurrentWidget(self.welcome_page)
        self.title_label.fade_in(800)
        QTimer.singleShot(300, lambda: self.desc_label.fade_in(800))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition() - self.drag_pos
            self.move(self.pos() + delta.toPoint())
            self.drag_pos = event.globalPosition()
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.video_player and self.video_player.current_frame and not self.video_player.current_frame.isNull():
            try:
                frame = self.video_player.current_frame
                video_w = frame.width()
                video_h = frame.height()
                if video_h == 0:
                    video_h = 1
                video_ratio = video_w / video_h
                window_ratio = self.width() / max(1, self.height())

                if window_ratio > video_ratio:
                    draw_height = self.height()
                    draw_width = int(draw_height * video_ratio)
                    x = (self.width() - draw_width) // 2
                    y = 0
                else:
                    draw_width = self.width()
                    draw_height = int(draw_width / video_ratio)
                    x = 0
                    y = (self.height() - draw_height) // 2

                scaled_frame = frame.scaled(draw_width, draw_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawImage(x, y, scaled_frame)
            except Exception as e:
                print("绘制视频帧异常:", e)

        super().paintEvent(event)


class AnimatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def fade_in(self, duration=500):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()


def main():
    app = QApplication(sys.argv)
    main_win = MainWindow()
    oobe = OOBEWindow(main_win)
    oobe.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
