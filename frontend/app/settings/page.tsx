"use client";

import { useState } from 'react';

export default function SettingsPage() {
  const [provider, setProvider] = useState('openai');
  const [apiKey, setApiKey] = useState('');
  const [status, setStatus] = useState('');

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus('Saving...');
    const token = localStorage.getItem('keyaz_token');
    if (!token) {
      setStatus('Not authenticated.');
      return;
    }

    const response = await fetch('/api/v1/api-keys/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ provider, api_key: apiKey }),
    });

    if (response.ok) {
      setStatus('API key saved successfully.');
      setApiKey('');
    } else {
      setStatus('Failed to save API key.');
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <div className="mb-8 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold">Settings</h1>
          <p className="text-slate-400">Save provider API keys securely for the AI agent.</p>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-lg shadow-slate-950/20">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-300">Provider</label>
            <select className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100" value={provider} onChange={(event) => setProvider(event.target.value)}>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="gemini">Gemini</option>
              <option value="groq">Groq</option>
              <option value="deepseek">DeepSeek</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300">API Key</label>
            <input
              className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-sky-500"
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="sk-..."
            />
          </div>

          <button className="rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400" type="submit">
            Save API Key
          </button>
        </form>
        {status && <p className="mt-4 text-sm text-slate-400">{status}</p>}
      </div>
    </div>
  );
}
