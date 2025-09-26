import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      <nav style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          height: '64px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
            <Link to="/dashboard" style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#0f172a',
              textDecoration: 'none',
              letterSpacing: '-0.025em'
            }}>
              Bug Tracker
            </Link>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Link to="/dashboard" style={{
                padding: '8px 14px',
                fontSize: '14px',
                fontWeight: '500',
                color: isActive('/dashboard') ? '#2563eb' : '#64748b',
                backgroundColor: isActive('/dashboard') ? '#eff6ff' : 'transparent',
                textDecoration: 'none',
                borderRadius: '6px',
                transition: 'all 0.2s'
              }}>
                Dashboard
              </Link>
              <Link to="/projects" style={{
                padding: '8px 14px',
                fontSize: '14px',
                fontWeight: '500',
                color: isActive('/projects') ? '#2563eb' : '#64748b',
                backgroundColor: isActive('/projects') ? '#eff6ff' : 'transparent',
                textDecoration: 'none',
                borderRadius: '6px',
                transition: 'all 0.2s'
              }}>
                Projects
              </Link>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              padding: '6px 12px',
              backgroundColor: '#f8fafc',
              borderRadius: '6px',
              fontSize: '14px',
              color: '#0f172a',
              fontWeight: '500'
            }}>
              {user?.username}
            </div>
            <button
              onClick={logout}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#64748b',
                backgroundColor: 'transparent',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '32px 24px'
      }}>
        {children}
      </main>
    </div>
  );
}