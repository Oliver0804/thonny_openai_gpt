# Thonny OpenAI GPT Assistant Plugin

This is an OpenAI GPT assistant plugin designed for Thonny IDE, providing intelligent chat and code analysis functionality.
![alt text](demo.png)

## Features

- Integrated GPT chat sidebar
- Code analysis and suggestions
- Adjustable AI model parameters
- Support for GPT-3.5 and GPT-4 models
- Save chat history
- Simple dialog mode

## Installation

### Method 1: Manual Installation

1. Copy the entire `thonny_openai_gpt` directory to one of the following locations:
   - `~/.thonny/plugins/` (user-specific installation)
   - Under `Lib/site-packages/` in the Thonny installation directory (global installation)

2. Restart Thonny IDE, the plugin will load automatically

### Method 2: Install from PyPI (Recommended)

1. In Thonny's Tools menu -> Manage packages, search for "thonny-openai-gpt" and install

## Usage

1. After installation, you can find the "GPT Chat" sidebar in the "View" menu
2. You can also find the "GPT Assistant (Dialog)" option in the "Tools" menu
3. The first time you use it, you need to set your OpenAI API key and restart Thonny

## Setting up API Key

1. In the GPT chat sidebar, click the ⚙️ button in the top right corner
2. Enter your OpenAI API key
3. The key will be encrypted and stored in the local configuration file

### How to Get an OpenAI API Key

1. Go to the [OpenAI API website](https://openai.com/api/)
2. Register or log in to your OpenAI account
3. Click the "Profile" icon in the upper right corner and select "View API keys"
4. Click the "Create new secret key" button
5. Name your key, then click "Create secret key"
6. Copy the generated API key (note that you can only view it once)
7. Paste this key into the settings of the Thonny OpenAI GPT Assistant Plugin

Note: The OpenAI API is a paid service, and you need to set up a payment method on the OpenAI platform. New users may receive a certain amount of free usage credits.

## System Requirements

- Thonny 3.0 or higher
- Python 3.7 or higher
- Network connection (for API calls)
- OpenAI API key

## License

MIT License

## Author

Oliver0804 - icetzsr@gmail.com

---

# Thonny OpenAI GPT 助手插件

這是一個為 Thonny IDE 設計的 OpenAI GPT 助手插件，提供智能聊天和程式碼分析功能。
![alt text](demo.png)
## 功能特色

- 集成 GPT 聊天側邊面板
- 程式碼分析和建議
- 可調整的 AI 模型參數
- 支援 GPT-3.5 和 GPT-4 模型
- 保存聊天歷史記錄
- 簡易對話框模式

## 安裝方法

### 方法 1: 手動安裝

1. 將整個 `thonny_openai_gpt` 目錄複製到以下位置之一：
   - `~/.thonny/plugins/`（用戶特定安裝）
   - Thonny 安裝目錄的 `Lib/site-packages/` 下（全域安裝）

2. 重啟 Thonny IDE，插件將自動載入


### 方法 2: 從 PyPI 安裝 (推薦)

1. 在 Thonny 的工具選單 -> 管理套件 中搜尋 "thonny-openai-gpt" 並安裝

## 使用方式

1. 安裝後，您可以在「檢視」選單中找到「GPT聊天」側邊面板
2. 也可以在「工具」選單中找到「GPT助手（對話框）」選項
3. 首次使用時，需要設定您的 OpenAI API 金鑰 重新啟動Thonny

## 設定 API 金鑰

1. 在 GPT 聊天側邊面板中，點擊右上角的 ⚙️ 按鈕
2. 輸入您的 OpenAI API 金鑰
3. 金鑰將加密儲存在本地配置檔案中

### 如何獲取 OpenAI API 金鑰

1. 前往 [OpenAI API 網站](https://openai.com/api/)
2. 註冊或登入您的 OpenAI 帳戶
3. 點擊右上角的「個人資料」圖示，選擇「View API keys」
4. 點擊「Create new secret key」按鈕
5. 為您的金鑰命名，然後點擊「Create secret key」
6. 複製生成的 API 金鑰（請注意，您只能查看一次）
7. 將此金鑰貼入 Thonny OpenAI GPT 助手插件的設定中

注意：OpenAI API 是一項付費服務，您需要在 OpenAI 平台上設定付款方式。新用戶可能會獲得一定額度的免費使用額度。

## 系統需求

- Thonny 3.0 或更高版本
- Python 3.7 或更高版本
- 網路連接（用於 API 呼叫）
- OpenAI API 金鑰

## 授權

MIT License

## 作者

Oliver0804 - icetzsr@gmail.com