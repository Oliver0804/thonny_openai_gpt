"""
Thonny OpenAI GPT 助手插件 - 主模組
"""

import sys
import logging
import os

# 添加自身到插件路徑中確保可以被找到
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    # 將 gpt_tool 模組導入到全局命名空間
    from thonny_openai_gpt.gpt_tool import load_plugin as gpt_load_plugin
except ImportError:
    try:
        # 嘗試相對導入
        from .gpt_tool import load_plugin as gpt_load_plugin
    except ImportError as e:
        print(f"無法導入 gpt_tool 模組: {e}")
        gpt_load_plugin = None

def load():
    """插件入口點 - 由 Thonny 調用"""
    if gpt_load_plugin:
        try:
            gpt_load_plugin()
        except Exception as e:
            print(f"載入 GPT 插件時出錯: {e}")
            import traceback
            traceback.print_exc()