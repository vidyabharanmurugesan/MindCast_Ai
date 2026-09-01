import { useState } from 'react';

const API_BASE = 'http://localhost:5000/api/v1';

const Login = ({ onLogin }: { onLogin: (user: any) => void }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('doctor@hospital.com');
  const [password, setPassword] = useState('doctor123');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email, password } 
        : { email, password, full_name: name };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (data.success) {
        onLogin(data.data.user);
      } else {
        setError(data.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Failed to connect to the server. Make sure the backend is running.');
    }
  };

  return (
    <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div className="card" style={{ width: '400px', textAlign: 'center' }}>
        <img src="/MindCastAi.jpeg" alt="MindCast Ai Logo" style={{ width: '120px', height: '120px', margin: '0 auto 16px auto', display: 'block', borderRadius: '12px' }} />
        <h2 className="header-title" style={{ textAlign: 'center' }}>MindCast Ai</h2>
        <p className="text-muted mb-4">
          {isLogin ? 'Enter clinician credentials to continue' : 'Create your medical staff login'}
        </p>

        {error && (
          <div style={{ padding: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--error-color)', borderRadius: '6px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex-col gap-4">
          {!isLogin && (
            <div>
              <label className="text-muted" style={{ display: 'block', marginBottom: '4px' }}>Full Name</label>
              <input 
                type="text" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                required 
              />
            </div>
          )}
          <div>
            <label className="text-muted" style={{ display: 'block', marginBottom: '4px' }}>Email Address</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
            />
          </div>
          <div>
            <label className="text-muted" style={{ display: 'block', marginBottom: '4px' }}>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
            />
          </div>

          <button type="submit" className="btn-primary mt-4">
            {isLogin ? '🔐 Log In' : '✅ Complete Registration'}
          </button>
        </form>

        <div className="mt-4 flex justify-center">
          <button 
            type="button" 
            className="btn-outline w-full"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
          >
            {isLogin ? '📝 Create New Account (Sign Up)' : '⬅ Back to Login'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
