import React, { useState } from 'react';
import Shell from './components/Shell';
import SetupPage from './pages/SetupPage';
import InterviewPage from './pages/InterviewPage';
import ReportPage from './pages/ReportPage';
import HistoryPage from './pages/HistoryPage';
import { mockInitialSessionData } from './api/mockApi';

export default function App() {
  const [activeTab, setActiveTab] = useState('setup');
  const [sessionData, setSessionData] = useState(mockInitialSessionData);

  const getStepInfo = () => {
    switch (activeTab) {
      case 'setup':
        return '步驟 1/3：參數設定';
      case 'interview':
        return '步驟 2/3：進行實戰面試';
      case 'report':
        return '步驟 3/3：評測與對答覆盤';
      case 'history':
        return '歷次練習紀錄';
      default:
        return '系統就緒';
    }
  };

  return (
    <div class="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-body">
      <Shell
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentStepInfo={getStepInfo()}
      />

      <main class="flex-1">
        {activeTab === 'setup' && (
          <SetupPage
            sessionData={sessionData}
            setSessionData={setSessionData}
            onStartInterview={() => setActiveTab('interview')}
          />
        )}

        {activeTab === 'interview' && (
          <InterviewPage
            sessionData={sessionData}
            setSessionData={setSessionData}
            onFinishInterview={() => setActiveTab('report')}
          />
        )}

        {activeTab === 'report' && (
          <ReportPage
            sessionData={sessionData}
            onReset={() => setActiveTab('setup')}
          />
        )}

        {activeTab === 'history' && (
          <HistoryPage
            onViewReport={() => setActiveTab('report')}
          />
        )}
      </main>
    </div>
  );
}
