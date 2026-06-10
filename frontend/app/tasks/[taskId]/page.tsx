"use client";

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

interface LogEntry {
  type: string;
  text?: string;
  image?: string;
  result?: string;
}

export default function TaskLivePage({ params }: { params: { taskId: string } }) {
  const router = useRouter();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [image, setImage] = useState<string | null>(null);
  const taskId = params.taskId;

  useEffect(() => {
    const token = localStorage.getItem('keyaz_token');
    if (!token) {
      router.push('/settings');
      return;
    }

    const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/browser/${taskId}?token=${token}`);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'screenshot') {
        setImage(`data:image/png;base64,${payload.image}`);
      }
      if (payload.type === 'log') {
        setLogs((current) => [...current, { type: 'log', text: payload.text }]);
      }
      if (payload.type === 'complete') {
        setLogs((current) => [...current, { type: 'complete', text: payload.result }]);
      }
    };
    ws.onerror = () => {
      setLogs((current) => [...current, { type: 'log', text: 'WebSocket connection error.' }]);
    };
    return () => {
      ws.close();
    };
  }, [taskId, router]);

  const lines = useMemo(() => logs.map((entry, index) => (
    <div key={index} className="whitespace-pre-wrap">{entry.text}</div>
  )), [logs]);

  return (
    <div className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Live Browser View</h1>
          <p className="text-slate-400">Task ID: {taskId}</p>
        </div>
      </div>
      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4">
          <div className="h-[640px] overflow-hidden rounded-3xl bg-slate-950">
            {image ? (
              <img src={image} alt="Live browser stream" className="h-full w-full object-contain" />
            ) : (
              <div className="flex h-full items-center justify-center text-slate-500">Waiting for live stream...</div>
            )}
          </div>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="text-lg font-semibold mb-4">Agent Console</h2>
          <div className="flex h-[640px] flex-col gap-2 overflow-y-auto rounded-3xl border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-200">
            {lines.length > 0 ? lines : <div className="text-slate-500">Waiting for agent logs...</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
