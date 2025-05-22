import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QFrame, QStackedWidget, QTextEdit, QPlainTextEdit,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup


# ───────────────────────────────────────── Groq Client ───────────────────────────────────────── #
class GroqClient:
    """
    Minimal Groq-API wrapper (OpenAI-compatible).
    Replace YOUR_GROQ_API_KEY with your real key.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def ask(self, context: str, question: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",          # current large model name
            "messages": [
                {
                    "role": "system",
                    "content": "Answer ONLY from the webpage content below:\n" + context
                },
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


# ─────────────────────────────── Helpers: table-to-Markdown ─────────────────────────────── #
def html_to_text_with_tables(html: str) -> str:
    """
    Convert HTML to plain text but render every <table> as a GitHub-style
    Markdown table so the AI can digest it easily.
    """
    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        # First row → header
        headers = [col.get_text(strip=True) for col in rows[0].find_all(["th", "td"])]
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Remaining rows
        for row in rows[1:]:
            cells = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
            md += "| " + " | ".join(cells) + " |\n"

        # Replace original table with its markdown string
        table.replace_with(BeautifulSoup(md, "html.parser"))

    return soup.get_text(separator="\n", strip=True)


# ──────────────────────────────────────── Main Window ──────────────────────────────────────── #
class ChromeLikeBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Chrome — HTML Inspector")
        self.setGeometry(100, 100, 1200, 800)

        # ── Groq client (put your key here) ──
        self.groq = GroqClient("API Key")   # ← replace

        # List that keeps full-HTML strings for every tag in the tag list
        self._element_html_store = []

        self.init_ui()

    # ──────────────────────────────── UI setup ─────────────────────────────── #
    def init_ui(self):
        self.setStyleSheet("background-color:#1e1e1e; color:white;")
        main_layout = QHBoxLayout(self)

        # ╭──────────────── Left panel ────────────────╮
        left_panel = QFrame(self)
        left_panel.setFixedWidth(int(self.width() * 0.30))
        left_panel.setStyleSheet("background-color:#2e2e2e;")
        left_layout = QVBoxLayout(left_panel)

        # URL controls
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (e.g. https://example.com)")
        self.go_button = QPushButton("Go")
        for w in (self.url_input, self.go_button):
            w.setStyleSheet("background-color:#3e3e3e; color:white; padding:6px;")
        self.go_button.clicked.connect(self.load_url)

        # Tag list
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet("background-color:#141414; color:white;")
        self.tag_list.itemClicked.connect(self.display_tag_html)

        # HTML display
        self.html_display = QTextEdit()
        self.html_display.setReadOnly(True)
        self.html_display.setStyleSheet("background-color:#ffffff; color:#000000;")

        # Assemble left panel
        left_layout.addWidget(QLabel("<b>Browser Controls</b>"))
        left_layout.addWidget(self.url_input)
        left_layout.addWidget(self.go_button)
        left_layout.addSpacing(10)
        left_layout.addWidget(QLabel("<b>Page Elements (tag + id)</b>"))
        left_layout.addWidget(self.tag_list, stretch=1)
        left_layout.addSpacing(10)
        left_layout.addWidget(QLabel("<b>Selected Element (HTML rendered)</b>"))
        left_layout.addWidget(self.html_display, stretch=2)

        # ╭──────────────── Right panel (viewer/chat) ────────────────╮
        right_container = QVBoxLayout()
        # Tabs
        self.web_button     = self._make_tab_btn("Web Viewer")
        self.content_button = self._make_tab_btn("Content Viewer")
        self.chat_button    = self._make_tab_btn("Chat")
        self.web_button.clicked.connect(lambda: self.switch_tab(0))
        self.content_button.clicked.connect(lambda: self.switch_tab(1))
        self.chat_button.clicked.connect(lambda: self.switch_tab(2))

        button_bar = QHBoxLayout()
        for b in (self.web_button, self.content_button, self.chat_button):
            button_bar.addWidget(b)

        # Stacked views
        self.stacked_widget = QStackedWidget()

        self.web_viewer = QWebEngineView()
        self.web_viewer.setUrl(QUrl("https://google.com"))
        self.web_viewer.loadFinished.connect(self.extract_page_html)

        self.content_viewer = QPlainTextEdit()
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setStyleSheet("background-color:#1e1e1e; color:white; padding:8px;")

        # Chat widget
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: none;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
        """)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a question about this page...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #2e2e2e;
                color: white;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #444;
            }
        """)

        self.chat_send = QPushButton("Send")
        self.chat_send.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)

        self.chat_send.clicked.connect(self.handle_chat)
        self.chat_input.returnPressed.connect(self.chat_send.click)

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input)
        input_row.addWidget(self.chat_send)

        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(input_row)

        # Add pages to stack
        for w in (self.web_viewer, self.content_viewer, self.chat_widget):
            self.stacked_widget.addWidget(w)

        # Default tab
        self.switch_tab(0)

        right_container.addLayout(button_bar)
        right_container.addWidget(self.stacked_widget)

        # Wrap right side in a white card for contrast
        right_frame = QFrame(self)
        right_frame.setStyleSheet("""QFrame{background:white; border-radius:12px; margin:30px; padding:10px;}""")
        right_frame.setLayout(right_container)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

    # ─────────────────────────────── Helpers ─────────────────────────────── #
    @staticmethod
    def _make_tab_btn(label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setStyleSheet("background:#3e3e3e; color:white; padding:8px;")
        return btn

    def switch_tab(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        colors = ("#007acc", "#3e3e3e")   # active, inactive
        for i, btn in enumerate((self.web_button, self.content_button, self.chat_button)):
            bg = colors[0] if i == index else colors[1]
            btn.setStyleSheet(f"background:{bg}; color:white; padding:8px;")

    # ─────────────────────────────── Browser logic ─────────────────────────────── #
    def load_url(self):
        url = self.url_input.text().strip()
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        if url:
            self.web_viewer.setUrl(QUrl(url))

    def extract_page_html(self):
        # Grab the full body HTML from the page
        self.web_viewer.page().runJavaScript(
            "document.body.innerHTML",
            self._process_page_html
        )

    def _process_page_html(self, html: str):
        """
        • Show cleaned text (with Markdown tables) in Content Viewer
        • Fill tag list with <tag id=...>
        """
        # Fill Content Viewer for AI context
        cleaned_text = html_to_text_with_tables(html)
        self.content_viewer.setPlainText(cleaned_text)

        # Build tag list
        self._element_html_store.clear()
        self.tag_list.clear()

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(True):
            tag_id = tag.get("id", "")
            label = f"<{tag.name}{f' id=\"{tag_id}\"' if tag_id else ''}>"
            item = QListWidgetItem(label)
            self.tag_list.addItem(item)
            self._element_html_store.append(str(tag))   # save full HTML

    # ─────────────────────────────── Tag click ─────────────────────────────── #
    def display_tag_html(self, item: QListWidgetItem):
        idx = self.tag_list.row(item)
        if 0 <= idx < len(self._element_html_store):
            html_fragment = self._element_html_store[idx]
            # Render the fragment (tables, images, etc.) on the left
            self.html_display.setHtml(html_fragment)

    # ─────────────────────────────── Chat logic ─────────────────────────────── #
    def handle_chat(self):
        question = self.chat_input.text().strip()
        if not question:
            return

        self.chat_display.append(f"<span style='color: #00afff;'><b>You:</b> {question}</span>")
        self.chat_display.append("<span style='color: gray;'><i>Thinking...</i></span>")
        self.chat_input.clear()

        try:
            context = self.content_viewer.toPlainText()
            answer = self.groq.ask(context, question)
            # Preserve line breaks / Markdown tables with <pre>
            self.chat_display.append(f"<pre><b>AI:</b>\n{answer}</pre>")
        except Exception as exc:
            self.chat_display.append(f"<span style='color:red;'>Error: {exc}</span>")


# ─────────────────────────────── Run the app ─────────────────────────────── #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChromeLikeBrowser()
    window.show()
    sys.exit(app.exec_())
