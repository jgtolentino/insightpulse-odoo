'use client';
import { useState } from 'react';

export default function Home() {
  const [url,setUrl]=useState('');
  const [loading,setLoading]=useState(false);
  const [result,setResult]=useState<{docs_url?:string, slug?:string}|null>(null);
  const base = process.env.NEXT_PUBLIC_GITTODOC_API || 'https://insightpulseai.net/gittodoc/api';

  async function createDocs() {
    setLoading(true); setResult(null);
    const u = new URL(base + '/ingest');
    u.searchParams.set('repo_url', url);
    const res = await fetch(u.toString(), { method:'POST' });
    const j = await res.json();
    setResult(j); setLoading(false);
  }

  return (
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Gittodoc</h1>
      <p className="mb-4 text-gray-600">Turn any GitHub repository into a documentation link for fast AI indexing.</p>
      <div className="flex gap-2">
        <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://github.com/owner/repo"
          className="border rounded px-3 py-2 flex-1"/>
        <button onClick={createDocs} disabled={loading} className="bg-black text-white rounded px-4 py-2">
          {loading? 'Creating…' : 'Create Docs'}
        </button>
      </div>
      {result?.docs_url && (
        <div className="mt-6">
          <div className="text-sm text-gray-700">Docs ready:</div>
          <a className="text-blue-600 underline" href={result.docs_url} target="_blank">{result.docs_url}</a>
        </div>
      )}
      <hr className="my-6"/>
      <h2 className="font-semibold mb-2">Try examples</h2>
      <div className="flex flex-wrap gap-2">
        {['fastapi/fastapi','pallets/flask','excalidraw/excalidraw','openai/openai-python'].map(x=>(
          <button key={x} onClick={()=>setUrl('https://github.com/'+x)} className="border rounded px-2 py-1">{x}</button>
        ))}
      </div>
    </main>
  );
}
