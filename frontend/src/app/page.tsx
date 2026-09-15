'use client';

import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Zap, RefreshCw, Play, Square, AlertTriangle, CheckCircle2, Server } from 'lucide-react';

interface FeatureDetail {
  ks_stat: number;
  p_value: number;
  wasserstein_dist: number;
  drift_score: number;
}

interface DriftData {
  drift_score: number;
  is_drifting: boolean;
  details: Record<string, FeatureDetail>;
}

interface RetrainRecord {
  version: string;
  timestamp: number;
  status: string;
  message: string;
}

export default function MLOpsDashboard() {
  const [data, setData] = useState<any>(null);
  const [retrainHistory, setRetrainHistory] = useState<RetrainRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionMessage, setActionMessage] = useState<string>('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchData = async () => {
    try {
      const res = await fetch(`${API_URL}/`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
      
      const historyRes = await fetch(`${API_URL}/retrain/history`);
      if (historyRes.ok) {
        const historyJson = await historyRes.json();
        setRetrainHistory(historyJson.history || []);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch gateway metrics', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleStartStream = async (drift: boolean) => {
    try {
      const res = await fetch(`${API_URL}/stream/start?drift=${drift}&delay_seconds=0.5`, { method: 'POST' });
      const json = await res.json();
      setActionMessage(json.message);
      fetchData();
    } catch (err) {
      setActionMessage('Failed to start traffic stream');
    }
  };

  const handleStopStream = async () => {
    try {
      const res = await fetch(`${API_URL}/stream/stop`, { method: 'POST' });
      const json = await res.json();
      setActionMessage(json.message);
      fetchData();
    } catch (err) {
      setActionMessage('Failed to stop stream');
    }
  };

  const handleManualRetrain = async () => {
    try {
      const res = await fetch(`${API_URL}/retrain`, { method: 'POST' });
      const json = await res.json();
      setActionMessage(`Retrain executed: ${json.record.message}`);
      fetchData();
    } catch (err) {
      setActionMessage('Failed to trigger retrain');
    }
  };

  const driftInfo: DriftData = data?.current_drift || { drift_score: 0, is_drifting: false, details: {} };
  const isDrifting = driftInfo.is_drifting;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Activity className="h-8 w-8 text-cyan-400 animate-pulse" />
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              MLStream Observability Engine
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">Real-Time Distributed MLOps & Statistical Concept Drift Monitor</p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            <Server className="h-4 w-4 text-slate-400" />
            <span className="text-slate-400">Broker:</span>
            <span className="text-cyan-400">{data?.kafka_broker || 'localhost:9092'}</span>
          </div>
          <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-emerald-400 font-semibold">GATEWAY ONLINE</span>
          </div>
        </div>
      </header>

      {/* Action Notification Toast */}
      {actionMessage && (
        <div className="mt-4 bg-cyan-950/80 border border-cyan-500/50 text-cyan-200 px-4 py-2 rounded-md text-sm flex justify-between items-center">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage('')} className="text-xs text-cyan-400 hover:underline">Dismiss</button>
        </div>
      )}

      {/* Control Bar */}
      <section className="my-6 bg-slate-900 p-4 rounded-xl border border-slate-800 flex flex-wrap gap-3 items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-300 mr-2">Stream Controls:</span>
          <button
            onClick={() => handleStartStream(false)}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-lg text-xs font-semibold transition"
          >
            <Play className="h-3.5 w-3.5" /> Start Normal Traffic
          </button>
          <button
            onClick={() => handleStartStream(true)}
            className="flex items-center gap-2 bg-amber-600 hover:bg-amber-500 text-white px-3.5 py-2 rounded-lg text-xs font-semibold transition"
          >
            <AlertTriangle className="h-3.5 w-3.5" /> Inject Concept Drift
          </button>
          <button
            onClick={handleStopStream}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-2 rounded-lg text-xs font-semibold transition"
          >
            <Square className="h-3.5 w-3.5 text-rose-400" /> Stop Stream
          </button>
        </div>

        <button
          onClick={handleManualRetrain}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Trigger Manual Retrain
        </button>
      </section>

      {/* Main Grid Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* Drift Status Card */}
        <div className={`p-5 rounded-xl border ${isDrifting ? 'bg-rose-950/40 border-rose-600/50' : 'bg-slate-900 border-slate-800'}`}>
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Drift Status</span>
            {isDrifting ? <ShieldAlert className="h-5 w-5 text-rose-500 animate-bounce" /> : <CheckCircle2 className="h-5 w-5 text-emerald-500" />}
          </div>
          <div className="mt-3">
            <span className={`text-2xl font-black ${isDrifting ? 'text-rose-400' : 'text-emerald-400'}`}>
              {isDrifting ? 'DRIFT BREACH' : 'STABLE'}
            </span>
            <p className="text-xs text-slate-400 mt-1">Threshold: p-val &lt; 0.05 & score &gt; 0.15</p>
          </div>
        </div>

        {/* Drift Score Meter */}
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Composite Drift Score</span>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-cyan-400">{driftInfo.drift_score}</span>
            <span className="text-xs text-slate-500">/ 1.0</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${driftInfo.drift_score > 0.15 ? 'bg-rose-500' : driftInfo.drift_score > 0.08 ? 'bg-amber-400' : 'bg-cyan-400'}`}
              style={{ width: `${Math.min(driftInfo.drift_score * 100, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Active Model Version */}
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Model Version</span>
          <div className="mt-3 flex items-center gap-2">
            <Zap className="h-6 w-6 text-indigo-400" />
            <span className="text-2xl font-bold text-slate-100">{data?.model_version || 'v1.0.0'}</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">RandomForest Classifier (5-Feature)</p>
        </div>

        {/* Traffic Simulation State */}
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Simulator Stream</span>
          <div className="mt-3 flex items-center gap-2">
            <span className={`h-3 w-3 rounded-full ${data?.stream_simulator?.active ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`}></span>
            <span className="text-lg font-bold text-slate-200">
              {data?.stream_simulator?.active ? (data?.stream_simulator?.drift_enabled ? 'Drifting Traffic' : 'Normal Traffic') : 'Stopped'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Rate: ~2 requests/sec</p>
        </div>
      </div>

      {/* Feature Breakdown Table & Retrain Log Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Feature Statistical Breakdown (2 cols) */}
        <div className="lg:col-span-2 bg-slate-900 p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" /> Real-Time Statistical Feature Distribution Test (Sliding Window: 50)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-3">Feature</th>
                  <th className="p-3">KS Statistic</th>
                  <th className="p-3">p-value</th>
                  <th className="p-3">Wasserstein Dist</th>
                  <th className="p-3">Drift Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {Object.keys(driftInfo.details || {}).length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-4 text-center text-slate-500 italic">
                      Insufficient traffic samples to calculate feature breakdown. Start the stream to observe!
                    </td>
                  </tr>
                ) : (
                  Object.entries(driftInfo.details).map(([fname, fdetail]) => (
                    <tr key={fname} className="hover:bg-slate-800/40">
                      <td className="p-3 font-semibold text-cyan-300">{fname}</td>
                      <td className="p-3 text-slate-300">{fdetail.ks_stat}</td>
                      <td className={`p-3 font-bold ${fdetail.p_value < 0.05 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {fdetail.p_value}
                      </td>
                      <td className="p-3 text-slate-300">{fdetail.wasserstein_dist}</td>
                      <td className={`p-3 font-bold ${fdetail.drift_score > 0.15 ? 'text-rose-400' : 'text-slate-300'}`}>
                        {fdetail.drift_score}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Retraining Execution Log (1 col) */}
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <RefreshCw className="h-4 w-4 text-indigo-400" /> Retraining History Audit Log
          </h3>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {retrainHistory.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No retraining events triggered yet.</p>
            ) : (
              retrainHistory.slice().reverse().map((rec, idx) => (
                <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-indigo-400">{rec.version}</span>
                    <span className="text-[10px] text-slate-500">{new Date(rec.timestamp * 1000).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-slate-300">{rec.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
