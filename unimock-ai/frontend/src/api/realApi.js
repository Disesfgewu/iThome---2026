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

export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor, persona, questionCount) {
  try {
    const payload = {
      target_school: targetSchool || '',
      target_major: targetMajor || '',
      interview_mode: '標準二階面試',
      candidate_profile: {
        applicant_name: '',
        high_school: '',
        autobiography: ''
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
      scores: data.radar_scores || {
        logic_structure: 0,
        major_relevance: 0,
        communication_clarity: 0,
        adaptability: 0
      },
      overall_feedback: data.overall_strategic_report || '',
      strengths: [],
      improvements: [],
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
