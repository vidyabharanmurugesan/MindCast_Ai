import { useState, useRef } from 'react';
import {  Upload } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/v1';

const Assessment = ({ }: { user?: any }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [patient, setPatient] = useState({
    id: 'PAT-1002',
    name: 'Jane Doe',
    age: '32',
    gender: 'Female'
  });
  const [results, setResults] = useState<string[]>([]);



  const logResult = (msg: string) => setResults(prev => [...prev, msg]);

  const startSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/assessment/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patient.id })
      });
      const data = await res.json();
      if (data.success) {
        setSessionId(data.data.session_id);
        logResult(`Started new session: ${data.data.session_id}`);
      }
    } catch (err) {
      logResult('Error starting session.');
    }
  };






  const handleFaceUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await uploadFace(e.target.files[0]);
    }
  };

  const uploadFace = async (file: File) => {
    if (!sessionId) {
      alert("Please start a session first.");
      return;
    }
    const formData = new FormData();
    formData.append('image', file);
    logResult('Uploading face image...');
    try {
      const res = await fetch(`${API_BASE}/assessment/${sessionId}/face`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        logResult(`[Face Prediction]: ${data.data.emotion} (${data.data.confidence}%)`);
      } else {
        logResult(`Error: ${data.message}`);
      }
    } catch (err) {
      logResult('Error communicating with server.');
    }
  };

  const handleVoiceUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!sessionId) {
      alert("Please start a session first.");
      return;
    }
    if (e.target.files && e.target.files[0]) {
      const formData = new FormData();
      formData.append('audio', e.target.files[0]);
      logResult('Uploading voice audio...');
      try {
        const res = await fetch(`${API_BASE}/assessment/${sessionId}/voice`, {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (data.success) {
          logResult(`[Voice Prediction]: ${data.data.emotion} (${data.data.confidence}%)`);
        } else {
          logResult(`Error: ${data.message}`);
        }
      } catch (err) {
        logResult('Error communicating with server.');
      }
    }
  };

  const finishSession = async () => {
    if (!sessionId) {
      alert("Please start a session first.");
      return;
    }
    try {
      logResult('Finishing session and generating report...');
      const res = await fetch(`${API_BASE}/assessment/${sessionId}/finish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_details: patient })
      });
      const data = await res.json();
      if (data.success) {
        logResult('================ CLINICAL REPORT GENERATED ================');
        logResult(`Report ID: ${data.data.report.report_id}`);
        logResult(`Overall Emotion: ${data.data.report.fused_clinical_result.overall_emotion}`);
        logResult(`Risk Level: ${data.data.report.fused_clinical_result.risk_level}`);
        logResult('=========================================================');
      } else {
        logResult(`Error: ${data.message}`);
      }
    } catch (err) {
      logResult('Error communicating with server.');
    }
  };

  return (
    <div className="flex gap-4" style={{ height: '100%' }}>
      {/* Left Panel */}
      <div className="flex-col gap-4" style={{ flex: 1 }}>
        <div className="card">
          <h3 className="subheader">1. Clinical Session Control</h3>
          <button className="btn-primary w-full" onClick={startSession}>
            Start New Assessment Session
          </button>
          <div className="text-muted mt-4">
            {sessionId ? `Active Session: ${sessionId}` : 'No active session'}
          </div>
        </div>

        <div className="card">
          <h3 className="subheader">2. Patient Details</h3>
          <div className="flex-col gap-2">
            <input 
              type="text" 
              placeholder="Patient ID" 
              value={patient.id} 
              onChange={e => setPatient({...patient, id: e.target.value})} 
            />
            <input 
              type="text" 
              placeholder="Patient Name" 
              value={patient.name} 
              onChange={e => setPatient({...patient, name: e.target.value})} 
            />
            <div className="flex gap-2">
              <input 
                type="number" 
                placeholder="Age" 
                value={patient.age} 
                onChange={e => setPatient({...patient, age: e.target.value})} 
              />
              <select 
                value={patient.gender} 
                onChange={e => setPatient({...patient, gender: e.target.value})}
              >
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="subheader">3. Emotion Media Inputs</h3>
          


          <label className="file-upload-btn w-full flex items-center justify-center gap-2 mb-2" style={{ cursor: 'pointer' }}>
            <Upload size={18} /> Upload Face Image
            <input type="file" accept="image/*" hidden onChange={handleFaceUpload} />
          </label>

          <label className="file-upload-btn w-full flex items-center justify-center gap-2" style={{ cursor: 'pointer' }}>
            <Upload size={18} /> Upload Voice Audio (.wav)
            <input type="file" accept="audio/*" hidden onChange={handleVoiceUpload} />
          </label>
        </div>

        <button className="btn-success w-full" style={{ padding: '16px', fontSize: '16px' }} onClick={finishSession}>
          Finish Session & Generate PDF Report
        </button>
      </div>

      {/* Right Panel */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <h3 className="subheader">Clinical Fusion Results</h3>
        <pre style={{ flex: 1, margin: 0 }}>
          {results.length === 0 ? 'Clinical multi-modal predictions will appear here upon media upload...\n' : results.join('\n')}
        </pre>
      </div>
    </div>
  );
};

export default Assessment;
