# 【Day 8】知識檢索：全方位履歷資料庫 Embedding 向量化、RAG 相似度比對與 Gemma-4-31B 出題引擎

在建立了 Day 7 的 Gemma-4-31B Chat Client、非同步 System Prompt 管理器與資安 Guardrail 之後，今天我們完成第二階段的關鍵樞紐——**全方位履歷資料庫向量化 (Candidate Profile Embedding)、RAG 相似度比對與動態題目生成引擎 (RAGRetrieverService)**。

---

## 1. 使用者提示詞 (User Prompt) 與核心資料結構模型

> 💬 **User Prompt**：
> 「根據 User 的資料輸入和對應的設定 我們也要根據 Profile 在生成問題的時候去根據 User data 進行 Embedding 並下去 RAG 資料庫進行 相似度比較。不只是個人經歷 競賽專案 目標學系 應該要包含所有的用戶資訊 包刮 自傳、經歷、成績、修課、社團幹部、專案競賽、得獎、專題論文 等等的領域 也就是出現在履歷中的資訊 都要可以洗出來並放好後 進行操作。」

根據這項關鍵需求，我們建立了收錄 8 大核心維度的 `CandidateProfile` 資料模型：

```python
class CandidateProfile(BaseModel):
    target_school: str = Field(default="")
    target_major: str = Field(default="")
    autobiography: str = Field(default="")
    experiences: List[str] = Field(default_factory=list)
    academic_performance: str = Field(default="")
    coursework: List[str] = Field(default_factory=list)
    club_leadership: List[str] = Field(default_factory=list)
    projects_and_awards: List[str] = Field(default_factory=list)
    thesis_and_research: str = Field(default="")
    certifications_and_skills: List[str] = Field(default_factory=list)

    def to_structured_text(self) -> str:
        """將 8 大履歷面向合成可進行向量化與 Prompt 注入的文字"""
        parts = [
            f"【目標校系】{self.target_school} {self.target_major}",
            f"【自傳摘要】{self.autobiography}" if self.autobiography else "",
            f"【歷程經歷】{'; '.join(self.experiences)}" if self.experiences else "",
            f"【學業成績】{self.academic_performance}" if self.academic_performance else "",
            f"【修課紀錄】{'; '.join(self.coursework)}" if self.coursework else "",
            f"【社團幹部】{'; '.join(self.club_leadership)}" if self.club_leadership else "",
            f"【專案競賽】{'; '.join(self.projects_and_awards)}" if self.projects_and_awards else "",
            f"【專題論文】{self.thesis_and_research}" if self.thesis_and_research else "",
            f"【證照技能】{'; '.join(self.certifications_and_skills)}" if self.certifications_and_skills else ""
        ]
        return "\n".join([p for p in parts if p.strip()])
```

---

## 2. RAG 檢索器與向量比對引擎 (`RAGRetrieverService`)

```python
class RAGRetrieverService:
    async def retrieve_sample_questions_for_candidate(
        self, candidate_profile: Union[str, CandidateProfile], target_major: Optional[str] = None, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """非同步估算 Candidate Profile 向量並進行 3072 維度向量比對"""
        profile_text = candidate_profile.to_structured_text() if isinstance(candidate_profile, CandidateProfile) else str(candidate_profile)
        query_text = f"目標學系: {target_major or ''}。\n【全方位履歷歷程】\n{profile_text}"
        
        query_vec = await asyncio.to_thread(embedding_service.embed_query, query_text)
        return question_repository.search_similar_questions_by_vector(query_vec=query_vec, department=target_major, top_k=top_k)

    async def generate_rag_question_for_candidate(
        self, candidate_profile: Union[str, CandidateProfile], target_school: str = "", target_major: str = "", **kwargs
    ) -> Dict[str, Any]:
        """端到端 RAG 出題：向量檢索 ➔ 注入 Prompt ➔ Gemma 4 生成專屬題目"""
        sample_qs = await self.retrieve_sample_questions_for_candidate(candidate_profile, target_major=target_major)
        rag_seed_context = self.format_rag_context_seeds(sample_qs)

        generated_question = await gemma_client.invoke_with_system_prompt(
            prompt_name="question_generation",
            target_school=target_school,
            target_major=target_major,
            candidate_profile=candidate_profile.to_structured_text() if isinstance(candidate_profile, CandidateProfile) else str(candidate_profile),
            sample_questions=rag_seed_context,
            **kwargs
        )
        return {"generated_question": generated_question, "rag_seed_questions": sample_qs}
```

---

## 3. 測試 Demo 與實機出題輸出紀錄 (Live Execution Demo & Output Logs)

執行全履歷 RAG 檢索與 Gemma-4-31B 動態出題端到端測試，產出成果：

- **RAG 檢索到的範例題庫種子 (Top Match)**：
  `"請向非資訊背景的人解釋什麼是 Stack 與 Queue？"` (類別: 技術專業型問題 | 難易度: 進階專業題)
- **Gemma-4-31B 實時動態合成之專屬面試考題**：
  > *「[考官]：小明同學，很高興看到你在全國資訊軟體競賽中能取得一等獎，並在專題論文中進行深度學習車牌辨識的研究... 假設你現在正在開發一個簡單的文字編輯器，需要實作『復原 (Undo, Ctrl+Z)』與『重做 (Redo, Ctrl+Y)』功能。請你告訴我，你會選擇哪些資料結構？並請試著將選擇邏輯解釋給完全沒有資訊背景的產品設計師聽...」*

---

## 4. Pytest 自動化測試驗證數據

```text
tests/test_rag_service.py::test_candidate_profile_model_structured_text PASSED               [ 25%]
tests/test_rag_service.py::test_full_resume_candidate_profile_vectorization PASSED            [ 50%]
tests/test_rag_service.py::test_rag_similarity_search_retrieval_with_candidate_profile PASSED [ 75%]
tests/test_rag_service.py::test_end_to_end_rag_question_generation_with_full_candidate_profile PASSED [100%]

============================== 4 passed in 26.14s ==============================
```

---

## 結語與明天預告

今天我們完成了涵蓋 **8 大核心履歷面向** 的全方位 RAG 檢索器與 User 資料向量化比對服務。

明天 **【Day 9】**，我們將進行 **LLM Client 429 退避重試與滑動視窗對話上下文管理**！
