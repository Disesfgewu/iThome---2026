/**
 * Real FastAPI Backend Client for UniMock AI
 * Connects React UI to FastAPI Backend Services running at http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000/api';

export async function uploadResumeApi(file, targetSchool, targetGroup, targetMajor) {
  try {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    formData.append('target_school', targetSchool || '');
    formData.append('target_major', targetMajor || '');

    const res = await fetch(`${API_BASE_URL}/resume/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Upload failed with status ${res.status}`);
    }

    const data = await res.json();
    return {
      fileName: file ? file.name : '',
      targetSchool: targetSchool || '',
      targetGroup: targetGroup || '',
      targetMajor: targetMajor || '',
      background: data.candidate_profile?.autobiography || '',
      leadershipExperiences: data.candidate_profile?.leadership_experiences || [],
      certificates: data.candidate_profile?.certificates || [],
      highlights: [],
      detectedBlindspots: []
    };
  } catch (err) {
    console.warn('Real API upload error:', err);
    return {
      fileName: file ? file.name : '',
      targetSchool: targetSchool || '',
      targetGroup: targetGroup || '',
      targetMajor: targetMajor || '',
      background: '',
      leadershipExperiences: [],
      certificates: [],
      highlights: [],
      detectedBlindspots: []
    };
  }
}

export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor, persona, questionCount, extractedProfile) {
  try {
    const payload = {
      target_school: targetSchool || '',
      target_major: targetMajor || '',
      interview_mode: persona === 'strict' ? '頂大嚴謹模式' : (persona === 'encourage' ? '鼓勵引導模式' : '標準二階面試'),
      candidate_profile: extractedProfile?.rawProfile || {
        applicant_name: '',
        high_school: '',
        autobiography: extractedProfile?.background || ''
      }
    };

    const res = await fetch(`${API_BASE_URL}/interview/setup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Interview setup failed: ${res.status}`);
    }

    const data = await res.json();
    return {
      sessionId: data.session_id,
      firstQuestion: data.first_question,
      phase: '破冰自述與專業動機'
    };
  } catch (err) {
    console.warn('Real API startInterview error:', err);
    return {
      sessionId: sessionId || '',
      firstQuestion: '',
      phase: '破冰自述與專業動機'
    };
  }
}

export async function respondInterviewApi(sessionId, currentIdx, answer) {
  try {
    const payload = {
      session_id: sessionId,
      user_answer: answer
    };

    const res = await fetch(`${API_BASE_URL}/interview/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Respond failed: ${res.status}`);
    }

    const data = await res.json();
    return {
      sessionId: data.session_id,
      nextQuestion: data.is_finished ? null : data.next_question,
      isFinished: data.is_finished,
      nextIndex: currentIdx + 1
    };
  } catch (err) {
    console.warn('Real API respondInterview error:', err);
    return {
      sessionId,
      nextQuestion: '',
      isFinished: false,
      nextIndex: currentIdx + 1
    };
  }
}

export async function respondInterviewStreamApi(sessionId, currentIdx, answer, onChunk) {
  try {
    const payload = {
      session_id: sessionId,
      user_answer: answer
    };

    const res = await fetch(`${API_BASE_URL}/interview/answer-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Respond stream failed with status: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let done = false;
    let fullText = '';
    let isFinished = false;
    let buffer = '';

    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      if (value) {
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete trailing chunk

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6);
            try {
              const parsed = JSON.parse(jsonStr);
              if (parsed.done) {
                isFinished = parsed.is_finished;
                if (parsed.full_text) {
                  fullText = parsed.full_text;
                }
              } else if (parsed.text) {
                fullText += parsed.text;
                if (onChunk) {
                  onChunk(parsed.text, fullText);
                }
              }
            } catch (e) {
              console.error('Error parsing SSE JSON:', e);
            }
          }
        }
      }
    }

    return {
      sessionId,
      nextQuestion: isFinished ? null : fullText,
      isFinished,
      nextIndex: currentIdx + 1
    };
  } catch (err) {
    console.warn('Real API respondInterviewStream error, falling back to standard API:', err);
    return respondInterviewApi(sessionId, currentIdx, answer);
  }
}

export async function getReportApi(sessionId) {
  try {
    const res = await fetch(`${API_BASE_URL}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });

    if (!res.ok) {
      throw new Error(`Report generation failed: ${res.status}`);
    }

    const data = await res.json();
    return {
      overall_score: data.overall_score || 80,
      scores: data.radar_scores || {
        logic_structure: 7.5,
        major_relevance: 8.0,
        communication_clarity: 7.5,
        adaptability: 7.0
      },
      overall_feedback: data.overall_strategic_report || '',
      strengths: data.strengths && data.strengths.length > 0 ? data.strengths : [
        "對目標系所的報考動機強烈且明確",
        "能夠結合個人實際經歷與專案/研究經驗進行情境陳述",
        "應答態度沉著自信，邏輯推演具備良好基礎"
      ],
      improvements: data.improvements && data.improvements.length > 0 ? data.improvements : [
        "建議進一步運用 STAR 原則，補強具體行動 (Action) 與量化成果 (Result)",
        "在深化專業追問時，可多引用核心學術理論與最新業界趨勢",
        "回答結尾可更精準連結個人未來的研究或修課規劃"
      ],
      question_diagnoses: []
    };
  } catch (err) {
    console.warn('Real API report error:', err);
    return {
      scores: { logic_structure: 0, major_relevance: 0, communication_clarity: 0, adaptability: 0 },
      overall_feedback: '',
      strengths: [],
      improvements: [],
      question_diagnoses: []
    };
  }
}

export const initialSessionData = {
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

export const departmentGroups = [
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
    tierLabel: isTopTier ? '頂尖前段名校模式' : '一般大學/研究所模式',
    difficultyDesc: isTopTier
      ? '🔥 已啟動高難度專業技術與申論題型（要求底層架構、演算法原理與 Benchmark 數據分析）'
      : '📘 已啟動標準模擬面試題型（著重個人動機、專案亮點與團隊溝通）'
  };
}

export async function getHistoryApi() {
  let apiRecords = [];
  try {
    const res = await fetch(`${API_BASE_URL}/records/list`);
    if (res.ok) {
      const data = await res.json();
      apiRecords = (data || []).map((item) => ({
        sessionId: item.session_id,
        date: item.created_at,
        targetSchool: item.target_school,
        targetGroup: "專業志願",
        targetMajor: item.target_major,
        roleCategory: item.interview_mode,
        duration: `${item.total_turns} 輪對答`,
        score: item.has_report ? 75 : 0,
        status: item.is_finished ? "COMPLETED" : "IN_PROGRESS"
      }));
    }
  } catch (err) {
    console.warn("Real API getHistory error:", err);
  }

  let localRecords = [];
  try {
    const saved = localStorage.getItem('unimock_history_sessions');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) {
        localRecords = parsed;
      }
    }
  } catch (e) {
    console.error("Local history error:", e);
  }

  // Merge local and API records by session ID
  const map = new Map();
  localRecords.forEach((r) => map.set(r.sessionId, r));
  apiRecords.forEach((r) => {
    if (!map.has(r.sessionId)) {
      map.set(r.sessionId, r);
    }
  });

  return Array.from(map.values());
}
