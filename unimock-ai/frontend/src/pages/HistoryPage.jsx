import React, { useState, useEffect } from 'react';
import { getHistoryApi } from '../api/mockApi';

export default function HistoryPage({ onViewReport }) {
  const [sessions, setSessions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    getHistoryApi().then((data) => setSessions(data));
  }, []);

  const filteredSessions = sessions.filter(
    (s) =>
      (s.targetSchool || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.targetGroup || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.targetMajor || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.roleCategory || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Header Section */}
      <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
        <div>
          <h2 class="text-3xl font-bold text-slate-900 tracking-tight mb-2">歷次練習紀錄</h2>
          <p class="text-slate-600 text-base max-w-2xl">
            查看您過去的 AI 模擬面試表現。系統會完整保留所有診斷報告，方便您追蹤進步軌跡。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <div class="relative w-full sm:w-64">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">
              search
            </span>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜尋學校、學群或學系..."
              class="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* History Table */}
      <div class="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 text-xs font-mono text-slate-500 uppercase tracking-wider">
                <th class="py-3.5 px-6">Date / Time</th>
                <th class="py-3.5 px-6">Target School & Major</th>
                <th class="py-3.5 px-6">Session Duration</th>
                <th class="py-3.5 px-6">Score</th>
                <th class="py-3.5 px-6">Status</th>
                <th class="py-3.5 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              {filteredSessions.map((item, idx) => (
                <tr key={idx} class="hover:bg-slate-50/80 transition-colors">
                  <td class="py-4 px-6">
                    <div class="font-mono font-bold text-slate-900">{item.date}</div>
                  </td>
                  <td class="py-4 px-6">
                    <div class="font-bold text-slate-900">
                      {item.targetSchool} · {item.targetMajor}
                    </div>
                    <div class="text-xs text-slate-500 mt-0.5">{item.targetGroup} ({item.roleCategory})</div>
                  </td>
                  <td class="py-4 px-6 font-mono text-slate-600">{item.duration}</td>
                  <td class="py-4 px-6">
                    <div class="flex items-center gap-2">
                      <span class={`font-mono font-bold ${
                        item.score >= 80 ? 'text-emerald-600' : item.score >= 70 ? 'text-amber-600' : 'text-rose-600'
                      }`}>
                        {item.score}
                      </span>
                      <div class="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div
                          style={{ width: `${item.score}%` }}
                          class={`h-full ${
                            item.score >= 80 ? 'bg-emerald-500' : item.score >= 70 ? 'bg-amber-500' : 'bg-rose-500'
                          }`}
                        />
                      </div>
                    </div>
                  </td>
                  <td class="py-4 px-6">
                    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-mono text-xs font-bold">
                      <span class="material-symbols-outlined text-xs">check_circle</span>
                      {item.status}
                    </span>
                  </td>
                  <td class="py-4 px-6 text-right">
                    <button
                      onClick={onViewReport}
                      class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold text-xs transition-colors shadow-2xs"
                    >
                      查看報告
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
