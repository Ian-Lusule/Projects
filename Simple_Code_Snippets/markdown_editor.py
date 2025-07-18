import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QSplitter, QFileDialog,
                             QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown2

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Editor with Live Preview")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Menu Bar
        self.menu_bar = QMenuBar()
        self.file_menu = QMenu("File", self)
        self.open_action = self.file_menu.addAction("Open")
        self.save_action = self.file_menu.addAction("Save")
        self.export_html_action = self.file_menu.addAction("Export to HTML")
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("Exit")

        self.menu_bar.addMenu(self.file_menu)
        self.setMenuBar(self.menu_bar)

        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.export_html_action.triggered.connect(self.export_html)
        self.exit_action.triggered.connect(self.close)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        # Markdown Editor
        self.markdown_editor = QTextEdit()
        self.splitter.addWidget(self.markdown_editor)

        # HTML Preview
        self.html_preview = QWebEngineView()
        self.splitter.addWidget(self.html_preview)

        # Connect text changed signal
        self.markdown_editor.textChanged.connect(self.update_preview)

        self.current_file = None

    def update_preview(self):
        markdown_text = self.markdown_editor.toPlainText()
        html = markdown2.markdown(markdown_text, extras=["fenced-code-blocks"])
        self.html_preview.setHtml(html)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.markdown_editor.setText(content)
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        if self.current_file:
            file_path = self.current_file
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", "Markdown Files (*.md)")
            if not file_path:
                return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.markdown_editor.toPlainText())
            self.current_file = file_path
            QMessageBox.information(self, "Success", "File saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def export_html(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to HTML", "", "HTML Files (*.html)")
        if file_path:
            try:
                html_content = self.html_preview.page().toHtml()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content())
                QMessageBox.information(self, "Success", "HTML exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export HTML: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec())