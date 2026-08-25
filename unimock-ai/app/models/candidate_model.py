from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CandidateProfile(BaseModel):
    """
    Comprehensive Candidate Resume & Application Portfolio Data Model.
    
    Encapsulates all 8 core dimensions of a candidate's high school / college application portfolio:
    1. 自傳 (Autobiography / Personal Statement)
    2. 經歷 (Work, Internship & Extracurricular Experiences)
    3. 成績 (Academic Grades, GPA & Ranking)
    4. 修課 (Coursework & Special Advanced Courses)
    5. 社團幹部 (Club & Leadership Positions)
    6. 專案競賽與得獎 (Projects, Competitions & Awards)
    7. 專題論文 (Research Papers, Graduation Thesis & Publications)
    8. 證照與技能 (Certifications & Technical/Language Skills)
    """
    target_school: str = Field(default="", description="目標學校，如：國立台灣大學")
    target_major: str = Field(default="", description="目標學系，如：資訊工程學系")
    target_group: str = Field(default="", description="目標學群，如：資訊電機學群")
    
    autobiography: str = Field(default="", description="自傳 / 個人陳述 (Autobiography)")
    experiences: List[str] = Field(default_factory=list, description="經歷列表 (工作、實習、志工與校外經歷)")
    academic_performance: str = Field(default="", description="成績與排名 (GPA, 班排%, 校排%)")
    coursework: List[str] = Field(default_factory=list, description="修課紀錄與核心科目 (特色修課、AP/IB/大學預修)")
    club_leadership: List[str] = Field(default_factory=list, description="社團與幹部經歷 (社長、幹部、組織經歷)")
    projects_and_awards: List[str] = Field(default_factory=list, description="專案、競賽與得獎紀錄")
    thesis_and_research: str = Field(default="", description="專題論文與研究成果 (小論文、專題報告)")
    certifications_and_skills: List[str] = Field(default_factory=list, description="證照與語言/程式技能 (TOEIC, APCS等)")

    def to_structured_text(self) -> str:
        """
        Synthesizes all 8 resume dimensions into a clean, comprehensive text format
        for Gemini Embedding 2 (3072 dims) vectorization and RAG prompt injection.
        """
        parts = [
            f"【目標校系】{self.target_school} {self.target_major} ({self.target_group})",
            f"【自傳摘要】{self.autobiography}" if self.autobiography else "",
            f"【歷程與經歷】{'; '.join(self.experiences)}" if self.experiences else "",
            f"【學業成績與排名】{self.academic_performance}" if self.academic_performance else "",
            f"【修課紀錄與核心科目】{'; '.join(self.coursework)}" if self.coursework else "",
            f"【社團與幹部經歷】{'; '.join(self.club_leadership)}" if self.club_leadership else "",
            f"【專案競賽與得獎】{'; '.join(self.projects_and_awards)}" if self.projects_and_awards else "",
            f"【專題論文與研究】{self.thesis_and_research}" if self.thesis_and_research else "",
            f"【證照與專業技能】{'; '.join(self.certifications_and_skills)}" if self.certifications_and_skills else ""
        ]
        return "\n".join([p for p in parts if p.strip()])
