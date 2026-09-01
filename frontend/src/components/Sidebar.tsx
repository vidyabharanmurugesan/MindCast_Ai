import { NavLink } from 'react-router-dom';
import { Stethoscope, Database, BrainCircuit, FileText } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <img src="/MindCastAi.jpeg" alt="MindCast Ai Logo" style={{ width: '32px', height: '32px', borderRadius: '4px' }} />
        <span>MindCast Ai</span>
      </div>
      <div className="nav-links">
        <NavLink 
          to="/assessment" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Stethoscope size={20} />
          Live Assessment
        </NavLink>
        <NavLink 
          to="/datasets" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Database size={20} />
          Dataset Inspector
        </NavLink>
        <NavLink 
          to="/training" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <BrainCircuit size={20} />
          AI Model Training
        </NavLink>
        <NavLink 
          to="/reports" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <FileText size={20} />
          Clinical Reports
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar;
