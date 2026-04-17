# 🏆 ShadPS4 Assistant — Trophy Sync Tool

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)

**ShadPS4 Assistant** — это мощная и удобная утилита для автоматической синхронизации трофеев из эмулятора **shadPS4** с вашей персональной базой данных. Идеальный инструмент для трофи-хантеров!

---

## 📸 Скриншоты
> *Здесь ты можешь вставить скриншот своей запущенной программы*
> `<img src="your_screenshot.png" width="400">`

---

## ✨ Ключевые фишки
* 🔍 **Авто-сканирование:** Автоматический поиск файлов `TROP.XML` во всех подпапках пользователя.
* 🔐 **Безопасный вход:** Авторизация через Google OAuth 2.0 (Device Flow) — быстро и надежно.
* ☁️ **Облачная база:** Мгновенная отправка прогресса (название игры, проценты, счетчик) в Firebase Firestore.
* 🌑 **Modern UI:** Лаконичный интерфейс в стиле "Dark Mode".

---

## 🛠 Установка и настройка

### 1. Подготовка кода
Клонируйте репозиторий и установите необходимые библиотеки:
```bash
git clone [https://github.com/Bestrigyn/shadPS4-assistant.git](https://github.com/Bestrigyn/shadPS4-assistant.git)
cd shadPS4-assistant
pip install requests
