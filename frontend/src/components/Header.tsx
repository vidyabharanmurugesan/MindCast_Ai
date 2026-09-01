import { LogOut, User } from 'lucide-react';

interface HeaderProps {
  user: {
    full_name: string;
    role: string;
  };
  onLogout: () => void;
}

const Header = ({ user, onLogout }: HeaderProps) => {
  return (
    <div className="topbar">
      <div className="flex items-center gap-2">
        <img src="/MindCastAi.jpeg" alt="MindCast Ai Logo" style={{ width: '28px', height: '28px', borderRadius: '4px' }} />
        <h2 className="header-title" style={{ fontSize: '18px', margin: 0 }}>MindCast Ai</h2>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-muted">
          <User size={18} />
          <span>Logged in: {user.full_name} ({user.role})</span>
        </div>
        <button onClick={onLogout} className="btn-outline flex items-center gap-2">
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Header;
