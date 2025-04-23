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