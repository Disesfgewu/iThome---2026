/**
 * Mock API Service Layer for UniMock AI
 * Cleaned structure: No default profile text pre-filled.
 */

export const mockInitialSessionData = {
  sessionId: "",
  targetSchool: "國立臺灣大學",
  targetGroup: "資訊電機學群",
  targetMajor: "資訊工程學系",
  interviewerPersona: "strict", // "strict" | "socratic"
  questionCount: 3,
  currentQuestionIndex: 0,
  isRecording: false,
  extractedProfile: {
    fileName: "",
    targetSchool: "",
    targetGroup: "",
    targetMajor: "",
    background: "",
    leadershipExperiences: [],
    certificates: [],
    highlights: [],
    detectedBlindspots: []
  },
  questions: [],
  dialogueHistory: [],
  evaluationReport: null
};

export const mockDepartmentGroups = [
  "資訊電機學群",
  "醫藥衛生學群",
  "數理化學學群",
  "工程學群",
  "管理學群",
  "財經學群",
  "外語學群",
  "人文社會學群",
  "生物資源學群",
  "建築與設計學群"
];

export function checkSchoolTier(schoolName) {
  const topTierKeywords = ['臺灣大學', '台大', '成功大學', '成大', '清華大學', '清大', '陽明交通大學', '交大', '政治大學', '政大', '臺灣科技大學', '臺科大', '中央大學', '中興大學', '中正大學', '中山大學'];
  const isTopTier = topTierKeywords.some(k => (schoolName || '').includes(k));
  return {
    isTopTier,
    tierLabel: isTopTier ? '頂尖前段名校模式' : '一般大學模式',
    difficultyDesc: isTopTier
      ? '🔥 已啟動高難度專業技術與申論題型（要求底層架構、演算法原理與 Benchmark 數據分析）'
      : '📘 已啟動標準模擬面試題型（著重個人動機、專案亮點與團隊溝通）'
  };
}

export const mockHistorySessions = [
  {
    sessionId: "sess_20260824_cs01",
    date: "2026-08-24 14:30",
    targetSchool: "國立臺灣大學",
    targetGroup: "資訊電機學群",
    targetMajor: "資訊工程學系",
    roleCategory: "頂尖名校二階模擬",
    duration: "25m 12s",
    score: 84,
    status: "COMPLETED"
  }
];

export async function uploadResumeApi(file, targetSchool, targetGroup, targetMajor) {
  await new Promise((r) => setTimeout(r, 600));
  return {
    fileName: file ? file.name : "",
    targetSchool: targetSchool || "",
    targetGroup: targetGroup || "",
    targetMajor: targetMajor || "",
    background: "",
    leadershipExperiences: [],
    certificates: [],
    highlights: [],
    detectedBlindspots: []
  };
}

export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor, persona, questionCount) {
  await new Promise((r) => setTimeout(r, 600));
  return {
    sessionId,
    firstQuestion: "",
    phase: "破冰自述與專業動機"
  };
}

export async function respondInterviewApi(sessionId, currentIdx, answer) {
  await new Promise((r) => setTimeout(r, 600));
  return {
    sessionId,
    nextQuestion: "",
    isFinished: false,
    nextIndex: currentIdx + 1
  };
}

export async function getReportApi(sessionId) {
  await new Promise((r) => setTimeout(r, 500));
  return null;
}

export async function getHistoryApi() {
  await new Promise((r) => setTimeout(r, 400));
  return mockHistorySessions;
}
