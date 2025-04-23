import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import json
import datetime
from pathlib import Path

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 只導入確定可用的函數
from thonny import get_workbench, get_shell

# 配置檔案路徑
CONFIG_DIR = os.path.join(str(Path.home()), ".thonny", "gpt_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# 預設配置
DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "chat_history": []
}

# 確保配置目錄存在
os.makedirs(CONFIG_DIR, exist_ok=True)

def get_editor_notebook():
    """獲取編輯器筆記本的替代方法"""
    wb = get_workbench()
    try:
        # Thonny 4.0 之後的方法
        editor_notebook = wb.get_editor_notebook()
        return editor_notebook
    except Exception:
        try:
            # 尋找編輯器筆記本的其他可能方法
            for attr_name in dir(wb):
                if 'editor' in attr_name.lower():
                    editor_obj = getattr(wb, attr_name)
                    if hasattr(editor_obj, 'get_current_editor'):
                        return editor_obj
        except Exception:
            pass
        
        print("無法獲取編輯器筆記本，某些功能可能無法正常工作")
        return None

def get_current_editor():
    """獲取當前編輯器的通用方法"""
    try:
        editor_notebook = get_editor_notebook()
        if editor_notebook:
            return editor_notebook.get_current_editor()
    except Exception:
        pass
    
    # 如果上面的方法失敗，嘗試從工作台直接獲取
    try:
        wb = get_workbench()
        if hasattr(wb, 'get_current_editor'):
            return wb.get_current_editor()
    except Exception:
        pass
    
    return None

def get_editor_text(editor):
    """從編輯器獲取文本的通用方法"""
    if not editor:
        return None
    
    try:
        # 嘗試多種可能的方法獲取編輯器文本
        methods = [
            lambda: editor.get_text_widget().get("1.0", tk.END),
            lambda: editor.get_text_content(),
            lambda: editor.get("1.0", tk.END),
            lambda: editor.text.get("1.0", tk.END),
            lambda: editor.get_code_view().get("1.0", tk.END),
            lambda: editor.get_content()
        ]
        
        for method in methods:
            try:
                code = method()
                if code:
                    return code
            except (AttributeError, TypeError):
                continue
    except Exception as e:
        print(f"獲取編輯器文本時發生錯誤: {e}")
    
    return None

def load_config():
    """載入配置檔案"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """儲存配置檔案"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

class GPTChatView(ttk.Frame):
    """GPT 聊天側邊面板"""
    
    # 添加靜態方法，用於從選單直接設定 API Key
    @classmethod
    def show_api_key_dialog(cls):
        """顯示 API Key 設定對話框（靜態方法，可從選單直接調用）"""
        config = load_config()
        api_key = config.get("api_key", "")
        
        new_api_key = simpledialog.askstring(
            "API 設定", 
            "請輸入 OpenAI API 金鑰:",
            initialvalue=api_key,
            show="*"
        )
        
        if new_api_key is not None:
            config["api_key"] = new_api_key
            save_config(config)
            messagebox.showinfo("設定已儲存", "API 金鑰已成功儲存！")
    
    def __init__(self, master):
        super().__init__(master)
        
        self.config = load_config()
        self.messages = self.config.get("chat_history", [])
        self.api_key = self.config.get("api_key", "")
        
        self.model_var = tk.StringVar(value=self.config.get("model", "gpt-3.5-turbo"))
        self.temp_var = tk.DoubleVar(value=self.config.get("temperature", 0.7))
        self.max_tokens_var = tk.IntVar(value=self.config.get("max_tokens", 1000))
        
        self._init_ui()
        self._load_chat_history()
        
    def _init_ui(self):
        """初始化使用者介面"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # 頂部控制區域
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 模型選擇
        ttk.Label(control_frame, text="模型:").pack(side=tk.LEFT, padx=(0, 5))
        model_menu = ttk.Combobox(control_frame, textvariable=self.model_var, 
                                 values=["gpt-3.5-turbo", "gpt-4"], width=12)
        model_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # 溫度控制
        ttk.Label(control_frame, text="溫度:").pack(side=tk.LEFT, padx=(0, 5))
        temp_scale = ttk.Scale(control_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                              variable=self.temp_var, length=80)
        temp_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        # 設定按鈕
        settings_button = ttk.Button(control_frame, text="⚙️", width=3, command=self._show_settings)
        settings_button.pack(side=tk.RIGHT, padx=5)
        
        # 清除按鈕
        clear_button = ttk.Button(control_frame, text="🗑️", width=3, command=self._clear_chat)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # 聊天顯示區域
        self.chat_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=20)
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # 底部輸入區域和按鈕
        input_frame = ttk.Frame(self)
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        # 輸入框
        self.input_field = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=40, height=4)
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_field.bind("<Control-Return>", self._send_message)
        
        # 按鈕框架
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        
        # 發送按鈕
        send_button = ttk.Button(button_frame, text="發送", command=self._send_message)
        send_button.pack(fill=tk.X, expand=True, pady=(0, 5))
        
        # 插入程式碼按鈕
        code_button = ttk.Button(button_frame, text="插入程式碼", command=self._insert_current_code)
        code_button.pack(fill=tk.X, expand=True)
        
        # 如果沒有設定API金鑰，顯示提示
        if not self.api_key:
            self.after(500, self._show_api_key_notice)
    
    def _show_api_key_notice(self):
        """顯示API金鑰未設定的提示"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "⚠️ 請點擊右上角的⚙️按鈕設定OpenAI API金鑰\n\n", "notice")
        self.chat_display.tag_configure("notice", foreground="red")
        self.chat_display.config(state=tk.DISABLED)
    
    def _show_settings(self):
        """顯示設定對話框"""
        api_key = simpledialog.askstring("API 設定", "請輸入OpenAI API金鑰:", 
                                         initialvalue=self.api_key, show="*")
        if api_key is not None:
            self.api_key = api_key
            self.config["api_key"] = api_key
            save_config(self.config)
            
            # 更新溫度和令牌數
            self.config["temperature"] = self.temp_var.get()
            self.config["max_tokens"] = self.max_tokens_var.get()
            self.config["model"] = self.model_var.get()
            save_config(self.config)
            
            messagebox.showinfo("設定已儲存", "API金鑰和設定已成功儲存")
    
    def _clear_chat(self):
        """清除聊天記錄"""
        if messagebox.askyesno("確認", "確定要清除所有聊天記錄嗎？"):
            self.messages = []
            self.config["chat_history"] = []
            save_config(self.config)
            
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
    
    def _load_chat_history(self):
        """載入聊天記錄"""
        self.chat_display.config(state=tk.NORMAL)
        
        for msg in self.messages:
            if msg["role"] == "user":
                self._display_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self._display_assistant_message(msg["content"])
                
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _send_message(self, event=None):
        """發送訊息到GPT"""
        if not OPENAI_AVAILABLE:
            messagebox.showerror("錯誤", "請安裝OpenAI套件: pip install openai")
            return
            
        if not self.api_key:
            messagebox.showerror("錯誤", "請先設定OpenAI API金鑰")
            return
            
        text = self.input_field.get("1.0", tk.END).strip()
        if not text:
            return
            
        # 清空輸入框
        self.input_field.delete("1.0", tk.END)
        
        # 顯示用戶訊息
        self._display_user_message(text)
        
        # 將用戶訊息加入對話歷史
        self.messages.append({"role": "user", "content": text})
        
        # 顯示等待訊息
        self.chat_display.config(state=tk.NORMAL)
        wait_msg_index = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, "GPT正在思考...\n\n", "waiting")
        self.chat_display.tag_configure("waiting", foreground="gray")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # 在新線程中調用API
        threading.Thread(target=self._call_openai_api, args=(wait_msg_index,)).start()
    
    def _call_openai_api(self, wait_msg_index):
        """調用OpenAI API"""
        try:
            # 使用正確的 API 版本
            try:
                # 判斷是舊版還是新版 API
                openai_version = getattr(openai, "__version__", "0.0.0")
                is_new_version = int(openai_version.split('.')[0]) >= 1
                
                if is_new_version:
                    # 新版 API (1.0.0 及以上)
                    client = openai.OpenAI(api_key=self.api_key)
                    response = client.chat.completions.create(
                        model=self.model_var.get(),
                        messages=self.messages,
                        temperature=self.temp_var.get(),
                        max_tokens=self.max_tokens_var.get()
                    )
                    assistant_response = response.choices[0].message.content
                else:
                    # 舊版 API (0.x.x)
                    openai.api_key = self.api_key
                    response = openai.ChatCompletion.create(
                        model=self.model_var.get(),
                        messages=self.messages,
                        temperature=self.temp_var.get(),
                        max_tokens=self.max_tokens_var.get()
                    )
                    assistant_response = response.choices[0].message.content
            except AttributeError:
                # 如果上面的嘗試失敗，嘗試直接使用新版 API
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model_var.get(),
                    messages=self.messages,
                    temperature=self.temp_var.get(),
                    max_tokens=self.max_tokens_var.get()
                )
                assistant_response = response.choices[0].message.content
            
            # 移除等待訊息
            self.chat_display.config(state=tk.NORMAL)
            wait_end_index = wait_msg_index + "+2l"
            self.chat_display.delete(wait_msg_index, wait_end_index)
            self.chat_display.config(state=tk.DISABLED)
            
            # 顯示助手回應
            self._display_assistant_message(assistant_response)
            
            # 將助手回應加入對話歷史
            self.messages.append({"role": "assistant", "content": assistant_response})
            
            # 保存聊天記錄
            self.config["chat_history"] = self.messages
            save_config(self.config)
            
        except Exception as e:
            # 移除等待訊息
            self.chat_display.config(state=tk.NORMAL)
            wait_end_index = wait_msg_index + "+2l"
            self.chat_display.delete(wait_msg_index, wait_end_index)
            
            # 顯示錯誤訊息
            self.chat_display.insert(tk.END, f"錯誤: {str(e)}\n\n", "error")
            self.chat_display.tag_configure("error", foreground="red")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)
    
    def _display_user_message(self, text):
        """顯示用戶訊息"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "👤 您: ", "user_prefix")
        self.chat_display.insert(tk.END, text + "\n\n", "user_msg")
        self.chat_display.tag_configure("user_prefix", foreground="blue", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("user_msg", foreground="black")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _display_assistant_message(self, text):
        """顯示助手訊息"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "🤖 GPT: ", "assistant_prefix")
        self.chat_display.insert(tk.END, text + "\n\n", "assistant_msg")
        self.chat_display.tag_configure("assistant_prefix", foreground="green", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("assistant_msg", foreground="black")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _insert_current_code(self):
        """插入當前編輯中的程式碼"""
        try:
            editor = get_current_editor()
            if editor:
                code = get_editor_text(editor)
                if code and code.strip():
                    # 將程式碼加到輸入框
                    current_text = self.input_field.get("1.0", tk.END).strip()
                    
                    if current_text:
                        current_text += "\n\n"
                    
                    current_text += "```python\n" + code + "```\n\n請分析這段程式碼：\n"
                    
                    self.input_field.delete("1.0", tk.END)
                    self.input_field.insert("1.0", current_text)
                else:
                    messagebox.showinfo("提示", "目前編輯器中沒有程式碼")
            else:
                messagebox.showinfo("提示", "請先打開一個程式碼檔案")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法獲取當前程式碼: {str(e)}")

# 簡單對話框模式的GPT助手
def gpt_assistant():
    """顯示簡單的GPT對話框"""
    if not OPENAI_AVAILABLE:
        messagebox.showerror("錯誤", "請安裝OpenAI套件: pip install openai")
        return
        
    config = load_config()
    api_key = config.get("api_key", "")
    
    if not api_key:
        api_key = simpledialog.askstring("API 設定", "請輸入OpenAI API金鑰:", show="*")
        if not api_key:
            return
        
        config["api_key"] = api_key
        save_config(config)
    
    # 獲取當前編輯器中的代碼
    code_context = ""
    editor = get_current_editor()
    
    if editor:
        code = get_editor_text(editor)
        if code and code.strip():
            use_code = messagebox.askyesno("程式碼分析", 
                                        "是否要將當前編輯器中的程式碼送給GPT分析？")
            if use_code:
                code_context = (f"以下是我的Python程式碼，請幫我分析：\n"
                             f"```python\n{code}\n```\n")
    
    # 顯示對話框
    prompt_text = code_context if code_context else ""
    prompt = simpledialog.askstring("GPT對話", "輸入你要問GPT的內容：",
                                 initialvalue=prompt_text)
    
    if prompt:
        try:
            # 判斷是舊版還是新版 API
            openai_version = getattr(openai, "__version__", "0.0.0")
            is_new_version = int(openai_version.split('.')[0]) >= 1
            
            model = config.get("model", "gpt-3.5-turbo")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 1000)
            
            # 根據版本使用對應的 API 方法
            if is_new_version:
                # 新版 API (1.0.0 及以上)
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                answer = response.choices[0].message.content
            else:
                # 舊版 API (0.x.x)
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                answer = response.choices[0].message.content
            
            # 顯示回覆
            result_dialog = tk.Toplevel()
            result_dialog.title("GPT 回應")
            result_dialog.geometry("600x400")
            
            # 建立回覆顯示框
            result_text = scrolledtext.ScrolledText(result_dialog, wrap=tk.WORD)
            result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            result_text.insert(tk.END, answer)
            result_text.config(state=tk.DISABLED)
            
            # 複製按鈕
            def copy_to_clipboard():
                result_dialog.clipboard_clear()
                result_dialog.clipboard_append(answer)
                messagebox.showinfo("已複製", "回應已複製到剪貼簿")
            
            copy_button = ttk.Button(result_dialog, text="複製到剪貼簿", command=copy_to_clipboard)
            copy_button.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("錯誤", str(e))