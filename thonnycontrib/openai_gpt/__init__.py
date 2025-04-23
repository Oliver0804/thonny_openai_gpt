"""
Thonny OpenAI GPT 助手插件 - 提供聊天面板和程式碼分析功能
"""

from thonny import get_workbench
from thonnycontrib.openai_gpt.gpt_tool import GPTChatView, gpt_assistant

def load_plugin():
    """載入插件，註冊命令和工具列按鈕"""
    print("Loading thonny-openai-gpt plugin...")  # 加入日誌輸出
    
    try:
        wb = get_workbench()
        
        # 註冊視圖
        wb.add_view(GPTChatView, "GPT聊天", "se")
        
        # 註冊命令 (同時加入選單項目)
        wb.add_command(
            command_id="gpt_assistant",
            menu_name="tools",
            command_label="GPT 助手對話",
            handler=gpt_assistant,
            include_in_toolbar=False,
            caption="GPT 助手對話"
        )
        
        # 添加設定 API Key 的選單項目
        wb.add_command(
            command_id="gpt_settings",
            menu_name="tools",
            command_label="設定 GPT API Key",
            handler=lambda: GPTChatView.show_api_key_dialog(),
            include_in_toolbar=False,
            caption="設定 GPT API Key"
        )
        
        print("thonny-openai-gpt plugin loaded successfully.")
    except Exception as e:
        print(f"Error loading thonny-openai-gpt plugin: {e}")
        import traceback
        traceback.print_exc()