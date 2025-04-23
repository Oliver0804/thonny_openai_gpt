"""
Thonny OpenAI GPT Assistant Plugin - Provides chat panel and code analysis capabilities
"""

import webbrowser
from thonny import get_workbench
from thonnycontrib.openai_gpt.gpt_tool import GPTChatView, gpt_assistant

def open_github_issues():
    """Open GitHub issues page"""
    webbrowser.open("https://github.com/Oliver0804/thonny_openai_gpt/issues")

def load_plugin():
    """Load plugin, register commands and toolbar buttons"""
    print("Loading thonny-openai-gpt plugin...")  # Add log output
    
    try:
        wb = get_workbench()
        
        # Register view - Use GPTChatView as view identifier for reference in code
        wb.add_view(GPTChatView, "GPT Chat", "se", default_position_key="se")
        
        # Register command (with concise description)
        wb.add_command(
            command_id="gpt_assistant",
            menu_name="tools",
            command_label="Open GPT Assistant",
            handler=gpt_assistant,
            include_in_toolbar=True,  # Add to toolbar for quick access
            caption="Analyze current code with GPT"
        )
        
        # Add API Key settings menu item
        wb.add_command(
            command_id="gpt_settings",
            menu_name="tools",
            command_label="Set GPT API Key",
            handler=lambda: GPTChatView.show_api_key_dialog(),
            include_in_toolbar=False,
            caption="Set GPT API Key"
        )
        
        # Add Report Issues menu item
        wb.add_command(
            command_id="gpt_report_issue",
            menu_name="tools",
            command_label="Report Issues",
            handler=open_github_issues,
            include_in_toolbar=False,
            caption="Report issues on GitHub"
        )
        
        print("thonny-openai-gpt plugin loaded successfully.")
    except Exception as e:
        print(f"Error loading thonny-openai-gpt plugin: {e}")
        import traceback
        traceback.print_exc()