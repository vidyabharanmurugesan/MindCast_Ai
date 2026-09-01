import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Login from './pages/Login';
import Assessment from './pages/Assessment';
import Datasets from './pages/Datasets';
import Training from './pages/Training';
import Reports from './pages/Reports';

const App = () => {
  const [user, setUser] = useState<{ full_name: string; role: string; email: string } | null>(null);
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = (userData: any) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (showSplash) {
    return (
      <div className="splash-screen">
        <img src="/MindCastAi.jpeg" alt="Loading MindCast Ai..." className="loading-logo" />
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Header user={user} onLogout={handleLogout} />
          <div className="page-container">
            <Routes>
              <Route path="/" element={<Navigate to="/assessment" replace />} />
              <Route path="/assessment" element={<Assessment user={user} />} />
              <Route path="/datasets" element={<Datasets />} />
              <Route path="/training" element={<Training />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;
