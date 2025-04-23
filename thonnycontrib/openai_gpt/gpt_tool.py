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

# Import only the necessary functions
from thonny import get_workbench, get_shell

# Configuration file paths
CONFIG_DIR = os.path.join(str(Path.home()), ".thonny", "gpt_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Default configuration
DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gpt-4.1-mini",  # Default model updated to gpt-4.1-mini
    "temperature": 0.7,
    "max_tokens": 1000,
    "chat_history": []
}

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Global variable to store GPTChatView reference for external function access
_global_gpt_chat_view = None

def get_editor_notebook():
    """Alternative method to get editor notebook"""
    wb = get_workbench()
    try:
        # Method for Thonny 4.0+
        editor_notebook = wb.get_editor_notebook()
        return editor_notebook
    except Exception:
        try:
            # Look for other possible methods to find editor notebook
            for attr_name in dir(wb):
                if 'editor' in attr_name.lower():
                    editor_obj = getattr(wb, attr_name)
                    if hasattr(editor_obj, 'get_current_editor'):
                        return editor_obj
        except Exception:
            pass
        
        print("Unable to get editor notebook, some features may not work properly")
        return None

def get_current_editor():
    """Generic method to get the current editor"""
    try:
        editor_notebook = get_editor_notebook()
        if editor_notebook:
            return editor_notebook.get_current_editor()
    except Exception:
        pass
    
    # If the above method fails, try getting it directly from the workbench
    try:
        wb = get_workbench()
        if hasattr(wb, 'get_current_editor'):
            return wb.get_current_editor()
    except Exception:
        pass
    
    return None

def get_editor_text(editor):
    """Generic method to get text from editor"""
    if not editor:
        return None
    
    try:
        # Try multiple possible methods to get editor text
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
        print(f"Error getting editor text: {e}")
    
    return None

def load_config():
    """Load configuration file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration file"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

class GPTChatView(ttk.Frame):
    """GPT Chat Side Panel"""
    
    # Add static method for setting API Key directly from menu
    @classmethod
    def show_api_key_dialog(cls):
        """Show API Key settings dialog (static method, can be called directly from menu)"""
        config = load_config()
        api_key = config.get("api_key", "")
        
        # Prepare masked version of API Key (if any)
        masked_key = ""
        if api_key:
            # Show only the first 5 and last 5 characters, replace middle with asterisks
            if len(api_key) <= 10:
                masked_key = api_key  # Show full if too short
            else:
                prefix = api_key[:5]
                suffix = api_key[-5:]
                stars = "*" * (len(api_key) - 10)  # Corrected formula for calculating number of asterisks
                masked_key = f"{prefix}{stars}{suffix}"
            
            message = f"Current API Key: {masked_key}\nEnter OpenAI API Key:"
        else:
            message = "Enter OpenAI API Key:"
        
        new_api_key = simpledialog.askstring(
            "API Settings", 
            message,
            initialvalue=api_key,
            show="*"
        )
        
        if new_api_key is not None:
            config["api_key"] = new_api_key
            save_config(config)
            messagebox.showinfo("Settings Saved", "API Key has been successfully saved!")
    
    def __init__(self, master):
        super().__init__(master)
        
        # Set global variable so other functions can access this instance
        global _global_gpt_chat_view
        _global_gpt_chat_view = self
        
        self.config = load_config()
        self.messages = self.config.get("chat_history", [])
        self.api_key = self.config.get("api_key", "")
        
        # Ensure model settings are correctly loaded
        self.model_var = tk.StringVar(value=self.config.get("model", DEFAULT_CONFIG["model"]))
        self.temp_var = tk.DoubleVar(value=self.config.get("temperature", DEFAULT_CONFIG["temperature"]))
        self.max_tokens_var = tk.IntVar(value=self.config.get("max_tokens", DEFAULT_CONFIG["max_tokens"]))
        
        self._init_ui()
        self._load_chat_history()
        
    def _init_ui(self):
        """Initialize user interface"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Top control area
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Model selection
        ttk.Label(control_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Update model options, add the latest OpenAI models
        model_menu = ttk.Combobox(control_frame, textvariable=self.model_var, 
                                 values=[
                                     "gpt-4.1-mini",  # Default model
                                     "o4-mini",       # 2025 inference model
                                     "gpt-4o",        # Multimodal flagship model
                                     "gpt-4o-mini",   # Lightweight version of GPT-4o
                                     "gpt-4.1",       # Updated version with better instruction following and long context
                                     "gpt-4-turbo",   # Faster GPT-4
                                     "gpt-4",         # Traditional GPT-4 model
                                     "o3",            # OpenAI o series
                                     "gpt-3.5-turbo"  # Older but still supported model
                                 ], 
                                 width=12)
        model_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # Temperature control
        ttk.Label(control_frame, text="Temperature:").pack(side=tk.LEFT, padx=(0, 5))
        temp_scale = ttk.Scale(control_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                              variable=self.temp_var, length=80)
        temp_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        # Settings button
        settings_button = ttk.Button(control_frame, text="⚙️", width=3, command=self._show_settings)
        settings_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        clear_button = ttk.Button(control_frame, text="🗑️", width=3, command=self._clear_chat)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=20)
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Bottom input area and buttons
        input_frame = ttk.Frame(self)
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=40, height=4)
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_field.bind("<Control-Return>", self._send_message)
        self.input_field.bind("<Return>", self._handle_return)
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        
        # Send button
        send_button = ttk.Button(button_frame, text="Send", command=self._send_message)
        send_button.pack(fill=tk.X, expand=True, pady=(0, 5))
        
        # Insert code button
        code_button = ttk.Button(button_frame, text="Insert Code", command=self._insert_current_code)
        code_button.pack(fill=tk.X, expand=True)
        
        # If API key is not set, show a notice
        if not self.api_key:
            self.after(500, self._show_api_key_notice)
    
    def _show_api_key_notice(self):
        """Show notice if API key is not set"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "⚠️ Please click the ⚙️ button in the top right to set the OpenAI API key\n\n", "notice")
        self.chat_display.tag_configure("notice", foreground="red")
        self.chat_display.config(state=tk.DISABLED)
    
    def _show_settings(self):
        """Show settings dialog"""
        # Prepare masked version of API Key
        masked_key = ""
        if self.api_key:
            # Show only the first 5 and last 5 characters, replace middle with asterisks
            if len(self.api_key) <= 10:
                masked_key = self.api_key  # Show full if too short
            else:
                prefix = self.api_key[:5]
                suffix = self.api_key[-5:]
                stars = "*" * (len(self.api_key) - 10)
                masked_key = f"{prefix}{stars}{suffix}"
            
            message = f"Current API Key: {masked_key}\nEnter OpenAI API Key:"
        else:
            message = "Enter OpenAI API Key:"
        
        api_key = simpledialog.askstring(
            "API Settings", 
            message,
            initialvalue=self.api_key, 
            show="*"
        )
        
        if api_key is not None:
            self.api_key = api_key
            self.config["api_key"] = api_key
            
            # Update other settings
            self.config["temperature"] = self.temp_var.get()
            self.config["max_tokens"] = self.max_tokens_var.get()
            self.config["model"] = self.model_var.get()
            save_config(self.config)
            
            messagebox.showinfo("Settings Saved", "API key and settings have been successfully saved")
    
    def _clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all chat history?"):
            self.messages = []
            self.config["chat_history"] = []
            save_config(self.config)
            
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
    
    def _load_chat_history(self):
        """Load chat history"""
        self.chat_display.config(state=tk.NORMAL)
        
        for msg in self.messages:
            if msg["role"] == "user":
                self._display_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self._display_assistant_message(msg["content"])
                
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _send_message(self, event=None):
        """Send message to GPT"""
        if not OPENAI_AVAILABLE:
            messagebox.showerror("Error", "Please install the OpenAI package: pip install openai")
            return
            
        if not self.api_key:
            messagebox.showerror("Error", "Please set the OpenAI API key first")
            return
            
        # Get original input text
        original_text = self.input_field.get("1.0", tk.END).strip()
        if not original_text:
            return
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Add context prefix to the text actually sent to API
        if "```python" in original_text or "analyze this code" in original_text:
            # If already contains code block, add Thonny IDE context
            prompt_prefix = "I am using Thonny IDE to write Python code. Here is the code I would like you to analyze or help with:"
            text_to_display = original_text
            text_to_send = f"{prompt_prefix}\n\n{original_text}"
        else:
            # General conversation content
            text_to_display = original_text
            text_to_send = original_text
        
        # Display user message (show original text, without prefix)
        self._display_user_message(text_to_display)
        
        # Add message with prefix to chat history
        self.messages.append({"role": "user", "content": text_to_send})
        
        # Show waiting message
        self.chat_display.config(state=tk.NORMAL)
        wait_msg_index = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, "GPT is thinking...\n\n", "waiting")
        self.chat_display.tag_configure("waiting", foreground="gray")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Call API in new thread
        threading.Thread(target=self._call_openai_api, args=(wait_msg_index,)).start()
    
    def _call_openai_api(self, wait_msg_index):
        """Call OpenAI API"""
        try:
            # Use correct API version
            try:
                # Determine if using old or new API version
                openai_version = getattr(openai, "__version__", "0.0.0")
                is_new_version = int(openai_version.split('.')[0]) >= 1
                
                if is_new_version:
                    # New API (1.0.0 and above)
                    client = openai.OpenAI(api_key=self.api_key)
                    response = client.chat.completions.create(
                        model=self.model_var.get(),
                        messages=self.messages,
                        temperature=self.temp_var.get(),
                        max_tokens=self.max_tokens_var.get()
                    )
                    assistant_response = response.choices[0].message.content
                else:
                    # Old API (0.x.x)
                    openai.api_key = self.api_key
                    response = openai.ChatCompletion.create(
                        model=self.model_var.get(),
                        messages=self.messages,
                        temperature=self.temp_var.get(),
                        max_tokens=self.max_tokens_var.get()
                    )
                    assistant_response = response.choices[0].message.content
            except AttributeError:
                # If above attempts fail, try using the new API directly
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model_var.get(),
                    messages=self.messages,
                    temperature=self.temp_var.get(),
                    max_tokens=self.max_tokens_var.get()
                )
                assistant_response = response.choices[0].message.content
            
            # Remove waiting message
            self.chat_display.config(state=tk.NORMAL)
            wait_end_index = wait_msg_index + "+2l"
            self.chat_display.delete(wait_msg_index, wait_end_index)
            self.chat_display.config(state=tk.DISABLED)
            
            # Display assistant response
            self._display_assistant_message(assistant_response)
            
            # Add assistant response to chat history
            self.messages.append({"role": "assistant", "content": assistant_response})
            
            # Save chat history
            self.config["chat_history"] = self.messages
            save_config(self.config)
            
        except Exception as e:
            # Remove waiting message
            self.chat_display.config(state=tk.NORMAL)
            wait_end_index = wait_msg_index + "+2l"
            self.chat_display.delete(wait_msg_index, wait_end_index)
            
            # Display error message
            self.chat_display.insert(tk.END, f"Error: {str(e)}\n\n", "error")
            self.chat_display.tag_configure("error", foreground="red")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)
    
    def _display_user_message(self, text):
        """Display user message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "👤 You: ", "user_prefix")
        self.chat_display.insert(tk.END, text + "\n\n", "user_msg")
        self.chat_display.tag_configure("user_prefix", foreground="blue", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("user_msg", foreground="black")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _display_assistant_message(self, text):
        """Display assistant message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "🤖 GPT: ", "assistant_prefix")
        self.chat_display.insert(tk.END, text + "\n\n", "assistant_msg")
        self.chat_display.tag_configure("assistant_prefix", foreground="green", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("assistant_msg", foreground="black")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _insert_current_code(self):
        """Insert current editor code"""
        try:
            editor = get_current_editor()
            if editor:
                code = get_editor_text(editor)
                if code and code.strip():
                    # Add code to input field
                    current_text = self.input_field.get("1.0", tk.END).strip()
                    
                    if current_text:
                        current_text += "\n\n"
                    
                    current_text += "```python\n" + code + "```\n\nPlease analyze this code:\n"
                    
                    self.input_field.delete("1.0", tk.END)
                    self.input_field.insert("1.0", current_text)
                else:
                    messagebox.showinfo("Info", "No code found in the current editor")
            else:
                messagebox.showinfo("Info", "Please open a code file first")
        except Exception as e:
            messagebox.showerror("Error", f"Could not get current code: {str(e)}")
    
    def prepare_code_analysis(self):
        """Prepare code analysis, insert code into input field and focus window if code exists"""
        editor = get_current_editor()
        if editor:
            code = get_editor_text(editor)
            if code and code.strip():
                # Add code to input field
                current_text = "```python\n" + code + "```\n\nPlease analyze this code:\n"
                
                self.input_field.delete("1.0", tk.END)
                self.input_field.insert("1.0", current_text)
                
                # Focus input field
                self.input_field.focus_set()
                
                # Ensure this panel is visible
                wb = get_workbench()
                wb.show_view("GPTChatView")
                
                return True
        return False

    def _handle_return(self, event):
        """Handle Enter key press event"""
        # Check if Enter key is pressed without Ctrl key
        if not (event.state & 0x0004):  # 0x0004 represents Control key
            # Get current text content
            text = self.input_field.get("1.0", tk.END).strip()
            
            # If content is not empty, send message
            if text:
                self._send_message()
                return "break"  # Prevent original Enter key behavior (newline)
            else:
                # If input field is empty, allow newline (normal behavior)
                return None
        # For Ctrl+Enter, keep original behavior (add newline)
        return None

# Simple dialog mode GPT assistant - now shows right panel instead
def gpt_assistant():
    """Show GPT assistant chat window (now shows right panel)"""
    global _global_gpt_chat_view
    
    if not OPENAI_AVAILABLE:
        messagebox.showerror("Error", "Please install the OpenAI package: pip install openai")
        return
    
    # If side panel is not yet created, ensure it's visible
    wb = get_workbench()
    wb.show_view("GPTChatView")
    
    # If side panel instance exists, use it directly
    if _global_gpt_chat_view:
        # Ask whether to analyze current code
        editor = get_current_editor()
        if editor:
            code = get_editor_text(editor)
            if code and code.strip():
                use_code = messagebox.askyesno("Code Analysis", 
                                         "Do you want to send the current editor code to GPT for analysis?")
                if use_code:
                    _global_gpt_chat_view.prepare_code_analysis()
    else:
        messagebox.showinfo("Info", "Please open the GPT Chat view first (from the View menu)")