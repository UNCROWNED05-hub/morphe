import { useEffect, useState } from 'react';
import { fetchHealth, fetchHello, type HealthResponse, type HelloResponse } from './api/client';
import { Activity, CheckCircle2, Server, Clock, AlertCircle } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [hello, setHello] = useState<HelloResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [healthData, helloData] = await Promise.all([
          fetchHealth(controller.signal),
          fetchHello(controller.signal)
        ]);
        setHealth(healthData);
        setHello(helloData);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          setError((err as Error).message || 'Failed to connect to backend server');
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();

    return () => {
      controller.abort();
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 selection:bg-indigo-500 selection:text-white">
      <main className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <header className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <span className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
              <Server className="w-6 h-6" />
            </span>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">System Scaffold</h1>
              <p className="text-xs text-slate-400">Phase 0: Baseline & Connectivity</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Activity className="w-3.5 h-3.5 animate-pulse" />
            Online
          </span>
        </header>

        <section className="space-y-4">
          {loading && (
            <div className="space-y-3 py-4">
              <div className="h-4 bg-slate-800 rounded animate-pulse w-3/4" />
              <div className="h-4 bg-slate-800 rounded animate-pulse w-1/2" />
            </div>
          )}

          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium">Connection Error</p>
                <p className="text-xs text-rose-300 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between p-3.5 bg-slate-800/50 rounded-xl border border-slate-700/50">
                <span className="text-slate-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> API Health
                </span>
                <span className="font-mono text-emerald-400 uppercase text-xs font-semibold tracking-wider">
                  {health?.status}
                </span>
              </div>

              <div className="flex items-center justify-between p-3.5 bg-slate-800/50 rounded-xl border border-slate-700/50">
                <span className="text-slate-400 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-indigo-400" /> Uptime
                </span>
                <span className="font-mono text-slate-200 text-xs">
                  {health ? `${health.uptime.toFixed(1)}s` : 'N/A'}
                </span>
              </div>

              <div className="p-3.5 bg-slate-800/50 rounded-xl border border-slate-700/50 space-y-1">
                <span className="text-slate-400 text-xs block">Server Response</span>
                <p className="text-slate-200 font-medium">{hello?.message}</p>
                <span className="text-[11px] text-slate-500 font-mono block">
                  {hello?.timestamp}
                </span>
              </div>
            </div>
          )}
        </section>

        <footer className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
          <span>React + Vite + TS</span>
          <span>Express API</span>
        </footer>
      </main>
    </div>
  );
}
