import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QPushButton, QLineEdit, QTextEdit, QVBoxLayout,
                             QWidget, QHBoxLayout, QScrollArea, QDialog,
                             QMessageBox, QFileDialog, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QTimer


class NoteEditDialog(QDialog):
    """Custom Dialog Window for Adding and Editing Notes with High-Contrast Dark Color Selection"""

    def __init__(self, parent=None, current_text="", current_color="#1E3A8A", is_dark=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Note" if current_text else "Add New Note")
        self.setFixedSize(480, 400)
        self.selected_color = current_color

        # High contrast / Dark color options for note cards
        self.color_options = [
            ("#1E3A8A", "Mavi"),
            ("#065F46", "Yeşil"),
            ("#581C87", "Mor"),
            ("#991B1B", "Kırmızı"),
            ("#78350F", "Kahve")
        ]

        bg_color = "#121212" if is_dark else "#2C3E50"
        text_bg = "#1E1E1E" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#1A1A1A"
        border_color = "#444444" if is_dark else "#BDC3C7"

        self.setStyleSheet(f"background-color: {bg_color}; color: white;")

        layout = QVBoxLayout(self)

        # Multi-line Text Input Area
        self.text_area = QTextEdit()
        self.text_area.setPlainText(current_text)
        self.text_area.setPlaceholderText("Type your note here...")
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {text_bg};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
                color: {text_color};
            }}
        """)
        self.text_area.textChanged.connect(self.update_char_count)
        layout.addWidget(self.text_area)

        # Character and Word Counter Label
        self.stats_label = QLabel("Words: 0 | Characters: 0")
        self.stats_label.setStyleSheet("color: #ECF0F1; font-size: 11px;")
        layout.addWidget(self.stats_label)

        # Color Selector Layout
        color_layout = QHBoxLayout()
        color_label = QLabel("Kart Rengi:")
        color_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
        color_layout.addWidget(color_label)

        self.color_group = QButtonGroup(self)
        for hex_code, name in self.color_options:
            btn = QRadioButton(name)
            btn.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
            if hex_code.upper() == self.selected_color.upper():
                btn.setChecked(True)
            self.color_group.addButton(btn)
            color_layout.addWidget(btn)
            btn.toggled.connect(lambda checked, h=hex_code: self.set_color(h) if checked else None)

        layout.addLayout(color_layout)

        # Action Buttons (Save & Cancel)
        button_layout = QHBoxLayout()

        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ECC71; color: white; }
        """)
        self.btn_save.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #E74C3C; color: white; }
        """)
        self.btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)

        self.update_char_count()

    def set_color(self, hex_code):
        self.selected_color = hex_code

    def update_char_count(self):
        text = self.text_area.toPlainText().strip()
        words = len(text.split()) if text else 0
        chars = len(text)
        self.stats_label.setText(f"Words: {words} | Characters: {chars}")

    def get_data(self):
        return self.text_area.toPlainText().strip(), self.selected_color


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note App")
        self.setGeometry(725, 150, 540, 800)

        self.is_dark_mode = False

        # Dynamically set file path in current working directory
        self.file_path = os.path.join(os.getcwd(), "nots.json")

        self.title_label = QLabel("-- Note App --")
        self.theme_button = QPushButton("🌙")
        self.export_button = QPushButton("💾 Export")
        self.clear_all_button = QPushButton("🗑️ Clear All")
        self.add_button = QPushButton("+")
        self.search_bar = QLineEdit()
        self.counter_label = QLabel("Total Notes: 0")

        self.empty_state_label = QLabel("📝 No notes found.\nClick + to add your first note!")

        self.initUI()
        self.apply_theme()

        # Automatic file management: Load existing or create new JSON
        self.ensure_json_exists_and_load()

    def show_message_box(self, icon, title, text, buttons=QMessageBox.Ok, default_button=QMessageBox.NoButton):
        """Custom styled QMessageBox that strictly obeys Dark/Light mode."""
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        if default_button != QMessageBox.NoButton:
            msg.setDefaultButton(default_button)

        bg_color = "#1E1E1E" if self.is_dark_mode else "#FFFFFF"
        text_color = "#FFFFFF" if self.is_dark_mode else "#1A1A1A"
        btn_bg = "#34495E" if self.is_dark_mode else "#BDC3C7"

        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {bg_color};
            }}
            QLabel {{
                color: {text_color};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: #FFFFFF;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #2980B9;
                color: #FFFFFF;
            }}
        """)
        return msg.exec_()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Layout (Title + Action Buttons)
        header_layout = QHBoxLayout()
        self.title_label.setAlignment(Qt.AlignCenter)

        self.theme_button.setFixedSize(36, 36)
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: #FFFFFF;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #3498DB; color: #FFFFFF; }
        """)
        self.export_button.clicked.connect(self.export_notes_to_txt)

        self.clear_all_button.setCursor(Qt.PointingHandCursor)
        self.clear_all_button.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: #FFFFFF;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #E74C3C; color: #FFFFFF; }
        """)
        self.clear_all_button.clicked.connect(self.clear_all_notes)

        header_layout.addWidget(self.export_button)
        header_layout.addWidget(self.clear_all_button)
        header_layout.addStretch()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_button)
        main_layout.addLayout(header_layout)

        # Search Bar
        self.search_bar.setPlaceholderText("🔍 Search notes...")
        self.search_bar.textChanged.connect(self.filter_notes)
        main_layout.addWidget(self.search_bar)

        # Dynamic Note Counter
        self.counter_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.counter_label)

        # Scrollable Area for Notes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")

        self.notes_widget = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_widget)
        self.notes_layout.setSpacing(10)

        # Empty State Placeholder Label
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("color: #95A5A6; font-size: 16px; font-weight: bold; padding: 40px;")
        self.notes_layout.addWidget(self.empty_state_label)

        self.notes_layout.addStretch()

        scroll_area.setWidget(self.notes_widget)
        main_layout.addWidget(scroll_area)

        # Bottom Add Button
        self.add_button.setFixedSize(60, 60)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_note)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button, alignment=Qt.AlignHCenter)
        main_layout.addLayout(button_layout)

    def apply_theme(self):
        """Applies theme styles across the application"""
        if self.is_dark_mode:
            bg_main = "#121212"
            text_title = "#FFFFFF"
            search_bg = "#1E1E1E"
            search_text = "#FFFFFF"
            search_border = "#444444"
            add_btn_bg = "#27AE60"
            add_btn_text = "#FFFFFF"
            self.theme_button.setText("☀️")
        else:
            bg_main = "#ECF0F1"
            text_title = "#2C3E50"
            search_bg = "#FFFFFF"
            search_text = "#2C3E50"
            search_border = "#BDC3C7"
            add_btn_bg = "#2980B9"
            add_btn_text = "#FFFFFF"
            self.theme_button.setText("🌙")

        self.setStyleSheet(f"background-color: {bg_main};")
        self.title_label.setStyleSheet(f"color: {text_title}; font-size: 26px; font-weight: bold;")
        self.counter_label.setStyleSheet(f"color: {text_title}; font-size: 12px; font-weight: bold;")

        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {search_bg};
                border: 2px solid {search_border};
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                color: {search_text};
            }}
        """)

        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #34495E;
                color: white;
                font-size: 16px;
                border-radius: 18px;
                border: none;
            }
            QPushButton:hover { background-color: #2C3E50; }
        """)

        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {add_btn_bg};
                color: {add_btn_text};
                font-size: 35px;
                font-weight: bold;
                border-radius: 30px;
                border: none;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)

        # Refresh styling on existing cards
        for i in range(self.notes_layout.count()):
            item = self.notes_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.empty_state_label:
                self.style_note_card(item.widget())

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def style_note_card(self, card):
        """Styles note cards with high-contrast text against dark colored card backgrounds"""
        is_pinned = getattr(card, "is_pinned", False)
        base_color = getattr(card, "card_color", "#1E3A8A")

        text_color = "#FFFFFF"
        date_color = "#E2E8F0"

        border = "3px solid #F1C40F" if is_pinned else "1px solid rgba(255,255,255,0.15)"

        card.setStyleSheet(f"""
            QWidget {{
                background-color: {base_color};
                border-radius: 10px;
                border: {border};
            }}
        """)

        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setStyleSheet(
                f"color: {text_color}; font-size: 15px; font-weight: 600; background: transparent; border: none;")
            labels[1].setStyleSheet(f"color: {date_color}; font-size: 11px; background: transparent; border: none;")

    def add_note_to_screen(self, text, date_str=None, is_pinned=False, color="#1E3A8A"):
        if not date_str:
            date_str = datetime.now().strftime("%d.%m.%Y %H:%M")

        note_card = QWidget()
        note_card.is_pinned = is_pinned
        note_card.card_color = color
        note_card.setCursor(Qt.PointingHandCursor)

        card_layout = QHBoxLayout(note_card)
        card_layout.setContentsMargins(14, 10, 14, 10)

        # Left side: Text & Date Layout
        left_layout = QVBoxLayout()

        text_label = QLabel(text)
        text_label.setWordWrap(True)

        date_label = QLabel(date_str)

        left_layout.addWidget(text_label)
        left_layout.addWidget(date_label)

        # Right side: Action Buttons Layout
        action_layout = QHBoxLayout()

        pin_button = QPushButton("📌" if is_pinned else "📍")
        pin_button.setFixedSize(28, 28)
        pin_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 12px;
                border-radius: 14px;
                border: none;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.4); }
        """)
        pin_button.clicked.connect(lambda: self.toggle_pin_note(note_card, pin_button))

        edit_button = QPushButton("✏️")
        edit_button.setFixedSize(28, 28)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 12px;
                border-radius: 14px;
                border: none;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.4); }
        """)
        edit_button.clicked.connect(lambda: self.edit_note(note_card, text_label, date_label))

        delete_button = QPushButton("✕")
        delete_button.setFixedSize(28, 28)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 14px;
                border: none;
            }
            QPushButton:hover { background-color: #C0392B; color: white; }
        """)
        delete_button.clicked.connect(lambda: self.delete_note(note_card))

        action_layout.addWidget(pin_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)

        card_layout.addLayout(left_layout)
        card_layout.addLayout(action_layout)

        note_card.mouseDoubleClickEvent = lambda event: self.edit_note(note_card, text_label, date_label)

        self.style_note_card(note_card)

        target_index = 0 if is_pinned else max(0, self.notes_layout.count() - 2)
        self.notes_layout.insertWidget(target_index, note_card)

        self.update_counter()

    def toggle_pin_note(self, note_card, pin_button):
        note_card.is_pinned = not note_card.is_pinned
        pin_button.setText("📌" if note_card.is_pinned else "📍")

        self.notes_layout.removeWidget(note_card)
        target_index = 0 if note_card.is_pinned else max(0, self.notes_layout.count() - 2)
        self.notes_layout.insertWidget(target_index, note_card)

        self.style_note_card(note_card)
        self.save_notes()

    def add_note(self):
        dialog = NoteEditDialog(self, is_dark=self.is_dark_mode)
        if dialog.exec_() == QDialog.Accepted:
            text, color = dialog.get_data()
            if text:
                self.add_note_to_screen(text, color=color)
                self.save_notes()

    def edit_note(self, note_card, text_label, date_label):
        current_text = text_label.text()
        current_color = getattr(note_card, "card_color", "#1E3A8A")

        dialog = NoteEditDialog(self, current_text, current_color, is_dark=self.is_dark_mode)
        if dialog.exec_() == QDialog.Accepted:
            new_text, new_color = dialog.get_data()
            if new_text:
                text_label.setText(new_text)
                note_card.card_color = new_color
                updated_date = datetime.now().strftime("%d.%m.%Y %H:%M") + " (Edited)"
                date_label.setText(updated_date)
                self.style_note_card(note_card)
                self.save_notes()

    def delete_note(self, note_card):
        response = self.show_message_box(
            QMessageBox.Question, 'Delete Note', "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if response == QMessageBox.Yes:
            note_card.deleteLater()
            QTimer.singleShot(100, lambda: (self.save_notes(), self.update_counter()))

    def clear_all_notes(self):
        if self.get_real_note_count() == 0:
            return

        response = self.show_message_box(
            QMessageBox.Warning, 'Clear All Notes', "Are you sure you want to delete ALL notes? This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if response == QMessageBox.Yes:
            for i in reversed(range(self.notes_layout.count())):
                item = self.notes_layout.itemAt(i)
                if item and item.widget() and item.widget() != self.empty_state_label:
                    item.widget().deleteLater()
            QTimer.singleShot(100, lambda: (self.save_notes(), self.update_counter()))

    def export_notes_to_txt(self):
        if self.get_real_note_count() == 0:
            self.show_message_box(QMessageBox.Information, "Export", "No notes available to export!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Notes", "my_notes.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("=== MY NOTES EXPORT ===\n\n")
                    for i in range(self.notes_layout.count()):
                        item = self.notes_layout.itemAt(i)
                        if item and item.widget() and item.widget() != self.empty_state_label:
                            labels = item.widget().findChildren(QLabel)
                            if len(labels) >= 2:
                                f.write(f"Date: {labels[1].text()}\n")
                                f.write(f"Note: {labels[0].text()}\n")
                                f.write("-" * 40 + "\n\n")
                self.show_message_box(QMessageBox.Information, "Export", "Notes successfully exported to TXT file!")
            except Exception as e:
                self.show_message_box(QMessageBox.Critical, "Error", f"Failed to export notes: {e}")

    def filter_notes(self, search_text):
        search_text = search_text.lower()
        visible_count = 0
        for i in range(self.notes_layout.count()):
            item = self.notes_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.empty_state_label:
                card = item.widget()
                labels = card.findChildren(QLabel)
                if labels:
                    note_text = labels[0].text().lower()
                    if search_text in note_text:
                        card.show()
                        visible_count += 1
                    else:
                        card.hide()
        self.counter_label.setText(f"Total Notes: {visible_count}")

    def get_real_note_count(self):
        count = 0
        for i in range(self.notes_layout.count()):
            item = self.notes_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.empty_state_label:
                count += 1
        return count

    def update_counter(self):
        count = self.get_real_note_count()
        self.counter_label.setText(f"Total Notes: {count}")
        if count == 0:
            self.empty_state_label.show()
        else:
            self.empty_state_label.hide()

    def save_notes(self):
        try:
            notes = []
            for i in range(self.notes_layout.count()):
                item = self.notes_layout.itemAt(i)
                if item and item.widget() and item.widget() != self.empty_state_label:
                    card = item.widget()
                    labels = card.findChildren(QLabel)
                    if len(labels) >= 2:
                        notes.append({
                            "text": labels[0].text(),
                            "date": labels[1].text(),
                            "pinned": getattr(card, "is_pinned", False),
                            "color": getattr(card, "card_color", "#1E3A8A")
                        })

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error while saving notes:", e)

    def ensure_json_exists_and_load(self):
        """Checks if nots.json exists; creates empty file if missing, then loads notes."""
        try:
            if not os.path.exists(self.file_path):
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)

            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    notes = json.load(f)
                except json.JSONDecodeError:
                    notes = []

                for item in notes:
                    if isinstance(item, dict):
                        self.add_note_to_screen(
                            item.get("text", ""),
                            item.get("date"),
                            item.get("pinned", False),
                            item.get("color", "#1E3A8A")
                        )
                    else:
                        self.add_note_to_screen(item)
        except Exception as e:
            print("Error while ensuring or loading JSON file:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())