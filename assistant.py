import os, json, glob, requests, webbrowser, threading, time
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

# ==========================================================
# [БЛОК НАСТРОЕК] ВСТАВЬТЕ ВАШИ ДАННЫЕ ИЗ FIREBASE/GOOGLE
# ==========================================================
# Инструкция:
# 1. PROJECT_ID - ID вашего проекта в консоли Firebase
# 2. FIREBASE_API_KEY - "Ключ API веб-приложения" из настроек проекта
# 3. CLIENT_ID и SECRET - создаются в Google Cloud Console (OAuth 2.0 Client IDs)

PROJECT_ID = "ВАШ_PROJECT_ID" 
FIREBASE_API_KEY = "ВАШ_API_KEY"
CLIENT_ID = "ВАШ_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET = "ВАШ_CLIENT_SECRET"

CONFIG_FILE = "config.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ==========================================================
# [БЛОК РАБОТЫ С КОНФИГОМ]
# ==========================================================
def load_cfg():
    base = {"path": "", "uid": "", "user": "НЕ АВТОРИЗОВАН", "idToken": ""}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**base, **json.load(f)}
        except: pass
    return base

config = load_cfg()

def save_cfg():
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)

# ==========================================================
# [БЛОК GOOGLE LOGIN] Авторизация
# ==========================================================
def start_google_login():
    if "ВАШ_" in CLIENT_ID:
        messagebox.showerror("Ошибка", "Сначала вставьте ваши ключи API в код!")
        return
    try:
        # Запрос кода устройства
        res = requests.post("https://oauth2.googleapis.com/device/code",
                            data={"client_id": CLIENT_ID, "scope": "openid profile email"},
                            timeout=10).json()

        dev_code, usr_code, v_url = res["device_code"], res["user_code"], res["verification_url"]

        login_win = tk.Toplevel(root)
        login_win.title("Вход в Google")
        login_win.geometry("350x280")
        tk.Label(login_win, text=f"ТВОЙ КОД:", font=("Arial", 12)).pack(pady=5)
        tk.Label(login_win, text=usr_code, font=("Arial", 22, "bold"), fg="#4285F4").pack(pady=10)
        tk.Button(login_win, text="1. ОТКРЫТЬ GOOGLE", bg="#4285F4", fg="white",
                  command=lambda: webbrowser.open(v_url), font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(login_win, text="2. ВВЕДИ КОД И ПОДТВЕРДИ", font=("Arial", 9)).pack()

        def poll():
            while True:
                time.sleep(5)
                try:
                    r = requests.post("https://oauth2.googleapis.com/token", data={
                        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                        "device_code": dev_code, "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                    }).json()

                    if "id_token" in r:
                        p_body = f"id_token={r['id_token']}&providerId=google.com"
                        l_res = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}",
                                             json={"postBody": p_body, "requestUri": "http://localhost", "returnSecureToken": True}).json()
                        
                        if "localId" in l_res:
                            config["uid"], config["idToken"] = l_res["localId"], l_res["idToken"]
                            config["user"] = f"АККАУНТ: {l_res.get('displayName', 'OK')}"
                            save_cfg()
                            root.after(0, lambda: [login_win.destroy(), refresh_ui(), messagebox.showinfo("!", "Вход выполнен!")])
                            break
                    if "error" in r and r["error"] not in ["authorization_pending", "slow_down"]: break
                except: continue
        threading.Thread(target=poll, daemon=True).start()
    except: messagebox.showerror("Ошибка", "Сеть недоступна")

# ==========================================================
# [БЛОК ТРОФЕЕВ] Поиск и отправка
# ==========================================================
def force_sync():
    uid, path, token = config.get("uid"), config.get("path"), config.get("idToken")
    if not uid or not token:
        messagebox.showwarning("!", "Войдите в аккаунт!")
        return
    if not path or not os.path.exists(path):
        messagebox.showwarning("!", "Укажите путь к папке эмулятора!")
        return

    earned, total, game = 0, 0, "Неизвестно"
    files = glob.glob(os.path.join(path, "**", "[Tt][Rr][Oo][Pp].[Xx][Mm][Ll]"), recursive=True)

    for f in files:
        try:
            rx = ET.parse(f).getroot()
            tn = rx.find('.//title-name')
            if tn is not None: game = tn.text
            for t in rx.findall('.//trophy'):
                total += 1
                if t.get('unlockstate') == "true": earned += 1
            if total > 0: break
        except: continue

    if total == 0:
        messagebox.showinfo("?", "Трофеи не найдены")
        return

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users/{uid}"
        payload = {"fields": {
            "game": {"stringValue": game},
            "perc": {"integerValue": str(round((earned / total) * 100))},
            "stat": {"stringValue": f"{earned}/{total}"}
        }}
        r = requests.patch(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200:
            messagebox.showinfo("ОК", f"Обновлено: {game}")
        else:
            messagebox.showerror("Ошибка", f"Код {r.status_code}. Проверьте ключи и базу!")
    except: messagebox.showerror("Ошибка", "Ошибка связи с базой")

# ==========================================================
# [БЛОК ИНТЕРФЕЙСА]
# ==========================================================
def refresh_ui():
    for w in root.winfo_children(): w.destroy()
    draw_ui()

def draw_ui():
    tk.Label(root, text="🏆 SHADPS4 ASSISTANT", font=("Arial", 14, "bold"), bg="#0A0A0A", fg="#00A2FF").pack(pady=20)
    u_color = "#00FF00" if config["uid"] else "white"
    tk.Label(root, text=config["user"], bg="#141414", fg=u_color, width=35, pady=5).pack(pady=5)

    if not config["uid"]:
        tk.Button(root, text="ВОЙТИ В АККАУНТ", bg="#4285F4", fg="white", width=25, command=start_google_login).pack(pady=10)
    else:
        tk.Button(root, text="СМЕНИТЬ АККАУНТ", bg="#333", fg="white", width=25,
                  command=lambda: [config.update({"uid": "", "idToken": "", "user": "НЕ АВТОРИЗОВАН"}), save_cfg(), refresh_ui()]).pack(pady=10)

    tk.Button(root, text="НАСТРОЙКИ ПУТИ", command=lambda: [config.update({"path": filedialog.askdirectory()}), save_cfg(), refresh_ui()], width=25).pack(pady=5)
    
    if config["path"]:
        tk.Label(root, text=f"Папка: {config['path'][-35:]}", font=("Arial", 8), bg="#0A0A0A", fg="gray").pack()

    tk.Button(root, text="ОБНОВИТЬ ТРОФЕИ", bg="#28a745", fg="white", height=2, font=("Arial", 11, "bold"), width=25, command=force_sync).pack(pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ShadPS4 Assistant")
    root.geometry("400x520")
    root.configure(bg="#0A0A0A")
    draw_ui()
    root.mainloop()
