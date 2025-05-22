# 🌐💬 Dynamic AI Webscrapper

![PyQt5](https://img.shields.io/badge/PyQt5-GUI-blue?style=for-the-badge)
![Groq AI](https://img.shields.io/badge/Groq%20AI-Chatbot-brightgreen?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=flat-square&logo=python)
![Status](https://img.shields.io/badge/Status-Working-success?style=flat-square)

> 🔍 **Browse websites. Scrape intelligently. Ask questions.**  
> A slick desktop app with a browser-style UI + Groq AI-powered content inspector.

---

## 🎯 What is it?

**Dynamic AI Webscrapper** is a smart desktop app that lets you:

✅ Browse any website using a mini Chrome-style interface  
🕵️ Extract and inspect HTML elements interactively  
🧠 Ask questions about the webpage content — powered by **Groq AI**  
📄 See structured HTML tables as Markdown for smarter parsing  
✨ Beautiful dark-themed UI with chat interface and multi-tab support

---

## 🚀 Features

| Feature                             | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| 🌍 Embedded Web Browser             | Built using `QWebEngineView` to render any live website                     |
| 🏷️ Tag-Based HTML Inspector        | Clickable tag list showing all elements like `<div id="...">`               |
| 📜 Rich HTML Viewer                | See selected HTML fragments rendered with images, tables, etc.              |
| 🤖 AI Q&A Panel                    | Groq-powered chatbot that answers ONLY using scraped webpage content        |
| 📋 Markdown Table Conversion       | Converts all `<table>` into AI-friendly Markdown format                     |
| 💡 Simple API Wrapper              | Minimal class to integrate Groq’s OpenAI-compatible endpoint                |

---

## 🎥 Preview

> 🖼️ Live Screenshot:
<p align="center">
  <img src="https://github.com/user-attachments/assets/3cb1da6c-078d-43b0-9db4-d92a90616401" width="800">
</p>

---

## 📦 Requirements

- Python `3.8+`
- `PyQt5`
- `PyQtWebEngine`
- `requests`
- `beautifulsoup4`

```bash
pip install PyQt5 PyQtWebEngine requests beautifulsoup4
