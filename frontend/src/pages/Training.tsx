import { useState } from 'react';
import { Zap } from 'lucide-react';

const API_BASE = 'https://mindcast-ai-server.onrender.com/api/v1';

const Training = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const trainModels = async () => {
    setLoading(true);
    setLogs(['Training models, please wait...']);
    
    try {
      // Train Face Model
      const faceRes = await fetch(`${API_BASE}/models/face/train`, { method: 'POST' });
      const faceData = await faceRes.json();
      
      let faceLog = '\n[Face Emotion CNN Model]\n';
      if (faceData.success) {
        faceLog += ` Model Type          : ${faceData.data.model_type}\n`;
        faceLog += ` Training Accuracy   : ${faceData.data.train_accuracy}%\n`;
        faceLog += ` Validation Accuracy : ${faceData.data.validation_accuracy}%\n`;
      } else {
        faceLog += ` Error: ${faceData.message}\n`;
      }
      setLogs(prev => [...prev, faceLog]);

      // Train Voice Model
      const voiceRes = await fetch(`${API_BASE}/models/voice/train`, { method: 'POST' });
      const voiceData = await voiceRes.json();
      
      let voiceLog = '\n[Voice Emotion 1D-CNN Model]\n';
      if (voiceData.success) {
        voiceLog += ` Model Type          : ${voiceData.data.model_type}\n`;
        voiceLog += ` Training Accuracy   : ${voiceData.data.train_accuracy}%\n`;
        voiceLog += ` Validation Accuracy : ${voiceData.data.validation_accuracy}%\n`;
      } else {
        voiceLog += ` Error: ${voiceData.message}\n`;
      }
      setLogs(prev => [...prev, voiceLog]);

    } catch (err) {
      setLogs(prev => [...prev, '\nError connecting to the server for training.']);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 className="subheader">Train Face & Voice CNN Models</h3>
      <button 
        className="btn-primary flex items-center justify-center gap-2 mb-4" 
        onClick={trainModels}
        disabled={loading}
      >
        <Zap size={18} /> {loading ? 'Training...' : 'Train Both AI Models & Calculate Accuracy'}
      </button>
      
      <pre style={{ flex: 1 }}>
        {logs.length === 0 ? 'Click the button above to start training.' : logs.join('\n')}
      </pre>
    </div>
  );
};

export default Training;
