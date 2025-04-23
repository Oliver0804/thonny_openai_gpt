# Thonny OpenAI GPT 助手插件

這是一個為 Thonny IDE 設計的 OpenAI GPT 助手插件，提供智能聊天和程式碼分析功能。

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

### 方法 2: 使用 pip 安裝

1. 建立 wheel 檔：
   ```bash
   python setup.py bdist_wheel
   ```

2. 安裝生成的 wheel 檔：
   ```bash
   
   
   ```

3. 重啟 Thonny IDE

### 方法 3: 從 PyPI 安裝 (如果已發布)

1. 在 Thonny 的工具選單 -> 管理套件 中搜尋 "thonny-openai-gpt" 並安裝
2. 或使用命令行：
   ```bash
   pip3 install -e /Users/oliver/code/thonny_openai_gpt
   ```

## 使用方式

1. 安裝後，您可以在「檢視」選單中找到「GPT聊天」側邊面板
2. 也可以在「工具」選單中找到「GPT助手（對話框）」選項
3. 首次使用時，需要設定您的 OpenAI API 金鑰

## 設定 API 金鑰

1. 在 GPT 聊天側邊面板中，點擊右上角的 ⚙️ 按鈕
2. 輸入您的 OpenAI API 金鑰
3. 金鑰將加密儲存在本地配置檔案中

## 系統需求

- Thonny 3.0 或更高版本
- Python 3.7 或更高版本
- 網路連接（用於 API 呼叫）
- OpenAI API 金鑰

## 授權

MIT License

## 作者

Oliver0804 - icetzsr@gmail.com