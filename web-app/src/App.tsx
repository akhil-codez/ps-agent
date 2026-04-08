import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingScreen from './components/LandingScreen';
import AuthScreen from './components/AuthScreen';
import MainApp from './components/MainApp';

function AppContent() {
  const { user, logout } = useAuth();
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      setTheme('light');
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleLogout = () => {
    logout();
  };

  const handleShowLanding = () => {
    logout();
    setShowAuth(false);
  };

  return (
    <div className="min-h-screen bg-base text-primary overflow-hidden">
      {!user && !showAuth && <LandingScreen onShowAuth={() => setShowAuth(true)} theme={theme} toggleTheme={toggleTheme} />}
      {!user && showAuth && <AuthScreen />}
      {user && <MainApp theme={theme} toggleTheme={toggleTheme} onLogout={handleLogout} onShowLanding={handleShowLanding} />}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
