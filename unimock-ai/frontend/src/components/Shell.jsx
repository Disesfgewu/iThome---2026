import React from 'react';

export default function Shell({ activeTab, setActiveTab, currentStepInfo }) {
  const navItems = [
    { id: 'setup', label: '面試設定', icon: 'settings_accessibility' },
    { id: 'interview', label: '實戰面試艙', icon: 'videocam' },
    { id: 'report', label: '評測診斷報告', icon: 'analytics' },
    { id: 'history', label: '歷次練習', icon: 'history' },
  ];

  return (
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50 w-full">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-md">
            <span class="material-symbols-outlined fill text-xl">robot_2</span>
          </div>
          <div>
            <h1 class="font-bold text-lg text-indigo-900 leading-none">UniMock AI</h1>
            <p class="text-xs text-slate-500 font-mono mt-0.5">智慧升學模擬面試系統</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav class="hidden md:flex items-center gap-1 h-full">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                class={`flex items-center gap-2 px-4 h-full border-b-2 font-medium text-sm transition-colors ${
                  isActive
                    ? 'border-indigo-600 text-indigo-600 font-semibold'
                    : 'border-transparent text-slate-600 hover:text-indigo-600 hover:border-slate-300'
                }`}
              >
                <span class={`material-symbols-outlined text-lg ${isActive ? 'fill' : ''}`}>
                  {item.icon}
                </span>
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Status Pills */}
        <div class="flex items-center gap-3">
          <span class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-mono">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            {currentStepInfo || '系統就緒'}
          </span>
          <div class="w-9 h-9 rounded-full bg-slate-200 border border-slate-300 overflow-hidden flex items-center justify-center text-slate-600">
            <span class="material-symbols-outlined text-xl">person</span>
          </div>
        </div>
      </div>
    </header>
  );
}
