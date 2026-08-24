# 【Day 27】防呆與例外處理：網路中斷、麥克風異常與模型重試機制

真實使用環境充滿各種突發狀況。今天我們要實作 **優雅降級（Graceful Degradation）** 與錯誤處理中介軟體。

---

## 1. 例外情境處理矩陣

| 異常情境 | 系統反應 | 解決/降級機制 |
| --- | --- | --- |
| **PDF 格式損壞** | 回傳 `400 Bad Request` | 提示使用者選擇有效 PDF 並提供備用純文字輸入 |
| **麥克風權限被拒** | STT 觸發 `not-allowed` 錯誤 | 切換為純文字打字模式並跳出通知 |
| **Gemma API 逾時** | 觸發重試機制 | 重試 3 次，若失敗轉由備用 Mock 題庫降級回應 |

---

## 2. 備用降級處理器範例 (`app/services/fallback_service.py`)

```python
class FallbackService:
    @staticmethod
    def get_fallback_question(target_major: str) -> str:
        return f"請先分享你在申請 {target_major} 時最重視的一項個人特質？"
```

---

## 結語與明天預告

今天我們完善了系統的防呆與例外容錯機制。

明天 **【Day 28】**，我們將進行全端效能調優，將端到端響應延遲控制在 1.5 秒以內！
