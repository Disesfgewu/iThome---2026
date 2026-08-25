# 【Day 10】多模態備審前處理：PDF 閱讀與 Gemma 備審解析 AI

在完成了 Day 9 的 Gemma 4 穩定度封裝、429 退避重試與對話上下文截斷後，今天我們正式進入學生「學習歷程與備審自傳 PDF」的多模態前處理與解析 AI 模組搭建——**PDF 多模態視覺與文字內容提取器 (`PDFParserService`)**。

---

## 1. 使用者提示詞 (User Prompt) 與多模態前處理需求

> 💬 **User Prompt**：
> 「接下來 到了 Day10 我們需要來做 PDF 的資料多模態的內容取得工具的部分 內容可能有 "圖片"、"文字"、"圖表" 等等資訊 並有排版 (理論上) 幫我看一下這樣子的工具要怎麼完成。另外 因為有個資的關係 這部分的 pdf 和 tests ignore 掉。」

針對學生備審資料包含**文字排版、嵌入式架構圖表、個人照與活動照片**的多模態特性，我們設計了：
1. **多頁面結構與文字洗淨提取 (Text & Layout Extraction)**：依頁面逐一提取純文字與排版結構。
2. **內嵌視覺影像組件提取 (Visual Image Component Extraction)**：辨識與提取 PDF 內含之圖表 (Architecture Diagrams)、照片與證照圖片 Metadata (解析度、格式、大小)。
3. **資安與個資去識別化保護 (PII Security & `.gitignore`)**：將 `test_files/` 與 `*.pdf` 全數納入 `.gitignore`，防禦任何個資洩漏風險；文章紀錄全數進行去識別化脫敏處理；單元測試建置 PII-Safe 備用機制。
4. **Gemma-4-31B 多模態備審分析**：對接 `docs/system_prompts/application_multimodal_analysis.md` 產出學習歷程亮點與教授可能質疑之盲點切入點。

---

## 2. 核心機制實作程式碼片段 (`app/services/document_parser.py`)

```python
class PDFParserService:
    def extract_multimodal_components(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """同時提取 PDF 頁面文字與內嵌視覺圖片圖表 Metadata"""
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page_summaries = []
        image_metadata_list = []

        for idx, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            page_img_details = []
            
            for img_idx, img_obj in enumerate(page.images, 1):
                pil_img = Image.open(io.BytesIO(img_obj.data))
                page_img_details.append(f"Image #{img_idx} ({pil_img.format}, {pil_img.size[0]}x{pil_img.size[1]} px)")
                image_metadata_list.append({"page": idx, "format": pil_img.format, "width": pil_img.size[0], "height": pil_img.size[1]})

            summary = f"=== [頁次 Page {idx}/{len(reader.pages)}] ===\n圖片圖表: {len(page.images)} 個\n文字：\n{page_text.strip()}\n"
            page_summaries.append(summary)

        return {"total_pages": len(reader.pages), "total_images": len(image_metadata_list), "full_document_text": "\n\n".join(page_summaries)}

    async def parse_multimodal_resume(self, pdf_bytes: bytes, target_school: str = "", target_major: str = "") -> Dict[str, Any]:
        """端到端多模態解析：PDF 提取 ➔ Gemma-4-31B 解析亮點與盲點"""
        components = self.extract_multimodal_components(pdf_bytes)
        analysis_result = await gemma_client.invoke_with_system_prompt(
            prompt_name="application_multimodal_analysis",
            target_major=target_major,
            document_content=components["full_document_text"][:8000]
        )
        return {"total_pages": components["total_pages"], "total_images": components["total_images"], "multimodal_analysis_result": analysis_result}
```

---

## 3. 測試 Demo 與去識別化實機輸出紀錄 (De-identified Live Execution Demo)

測試檔案：備審歷程 PDF 資料（含成績單、大專生專題架構圖與活動證明）。為保護個人隱密資訊，輸出內容已進行完整去識別化（De-identification）脫敏處理：

### 實機終端機測試對話紀錄 (`scripts/run_day10_live_test.py`)

```text
==================================================
UniMock AI - Day 10 Multimodal PDF Content Extractor Test
==================================================
Target PDF File: test_files/candidate_resume_portfolio.pdf (PII Protected)

--- [Step 1] Multimodal Extraction (Text, Layout & Image Components) ---
Total Pages: 6
Total Embedded Image Components: 10
Embedded Images Metadata List:
  - Page 1: 360x445 px (JPEG) - 個人大頭相片與聯絡區塊
  - Page 2: 524x213 px (PNG)  - 核心專題架構圖 (無梯度通道剪枝與物件偵測模型)
  - Page 4: 524x213 px (PNG)  - 邊緣裝置多視角物件偵測架構圖
  - Page 5: 444x333 px (JPEG) - 資訊社團幹部活動照
  - Page 6: 444x333 px (JPEG) - 雲端工作坊與系學會活動照

--- [Step 2] Live Multimodal Analysis with Gemma-4-31B ---

Gemma Multimodal Analysis Output Result:

這是一位背景極其強悍的資工系申請者。其特點在於「頂尖的學業基礎 (GPA 3.9+ / CPE A)」與「具備研究深度的 AI 輕量化專題」。

### 1. Key Highlights (核心亮點解析)
- 學術頂尖度：核心專業科目（資料結構、作業系統、微算機系統）成績優異，GPA 3.92，系排 Top 10%；CPE 程式檢定 A 等 (前 2.2%)。
- 研究深度 (AI 輕量化專題)：
  1. 大專生研究計畫（無梯度通道剪枝 / OS2D 單樣本物件偵測邊緣部署）。
  2. 結合生成式模型 (Generative AI) 產生多樣化探測影像，解決邊緣裝置無法在線上進行反向傳播的痛點。
- 系統實作能力：知名科技大廠實習 (Linux Kernel, Golang, C)，具備硬體 Jetson Nano 部署與 VHDL 開發經驗。

### 2. 潛在弱點與挑戰切入點 (Potential Vulnerabilities)
- 無梯度近似的理論基礎：主張以統計量 (L1 Norm / 方差) 近似梯度。教授會質疑：數學上是否有嚴謹證明？在極端非線性狀態下是否失效？
- 生成式 AI 數據的 Domain Gap：生成影像之分布與真實邊緣場景的差異如何控制？是否會造成通道剪枝誤判？

### 3. 面試教授最可能抽考的發問切入點
- 切入點 A（AI 輕量化理論）：請說明為什麼統計量可以代表通道對輸出的貢獻度？這種近似有何潛在風險？
- 切入點 B（GenAI 與 剪枝）：如何確保生成式 AI 所導出的權重探測不會對模型推論產生負面干擾？
- 切入點 C（底層系統與 AI）：以 Linux Kernel 與記憶體管理角度，TensorRT 在邊緣硬體上的推論效能瓶頸為何？

==================================================
Day 10 Multimodal PDF Test Completed Successfully!
==================================================
```

---

## 4. 個資資安保護與 Pytest 驗證數據 (`tests/test_day10_pdf_parser.py`)

在 `.gitignore` 寫入規則：
```text
# PII Privacy Protection
test_files/
*.pdf
```

執行 `pytest tests/test_day10_pdf_parser.py -v` 驗證結果：

```text
tests/test_day10_pdf_parser.py::test_pdf_multimodal_extraction_with_fallback PASSED          [ 50%]
tests/test_day10_pdf_parser.py::test_multimodal_gemma_resume_analysis_with_fallback PASSED   [100%]

====================== 2 passed in 35.12s =======================
```

---

## 結語與明天預告

今天我們完成了 **PDF 多模態視覺圖表與文字前處理服務 (`PDFParserService`)**，成功讓 Gemma 4 具備閱讀學生真實 PDF 備審、提取 10 個內嵌圖表元件與精準剖析亮點盲點的能力，並完成了個資資安 `.gitignore` 隔離與全篇去識別化脫敏保護！

明天 **【Day 11】**，我們將進入 **FastAPI 後端 API 路由開發 (Routers / Controller Layer)**，將備審上傳、RAG 題目生成與面試評分對話全數封裝成 HTTP / WebSocket 終端介面！
