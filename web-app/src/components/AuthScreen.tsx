import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, Languages, Bell, ShieldCheck,
  Smartphone, Lock, Eye, EyeOff, ArrowRight,
  User, MapPin, BarChart2, IndianRupee, Calendar, Users,
  Loader2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { register } from '../services/api';

const DISTRICTS = [
  'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha',
  'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad',
  'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod'
];

const CATEGORIES = ['General', 'OBC', 'SC', 'ST'];

export default function AuthScreen() {
  const { login, isLoading } = useAuth();
  const [view, setView] = useState<'login' | 'signup'>('login');
  
  const [loginPhone, setLoginPhone] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState<string | null>(null);
  
  const [signupData, setSignupData] = useState({
    name: '',
    phone: '',
    password: '',
    district: '',
    category: '',
    income: '',
    age: '',
    family_size: '1',
    language: 'malayalam'
  });
  const [signupError, setSignupError] = useState<string | null>(null);
  const [isSignupLoading, setIsSignupLoading] = useState(false);
  const [isLoginLoading, setIsLoginLoading] = useState(false);

  const handleLogin = async () => {
    if (!loginPhone || !loginPassword) {
      setLoginError('Please fill in all fields');
      return;
    }
    setLoginError(null);
    setIsLoginLoading(true);
    try {
      const result = await login(loginPhone, loginPassword);
      if (!result.success) {
        setLoginError(result.error || 'Login failed');
      }
    } finally {
      setIsLoginLoading(false);
    }
  };

  const handleSignup = async () => {
    const { name, phone, password, district, category, income, age, family_size } = signupData;
    if (!name || !phone || !password || !district || !category || !income || !age) {
      setSignupError('Please fill in all fields');
      return;
    }
    setSignupError(null);
    setIsSignupLoading(true);
    
    try {
      const result = await register({
        name,
        phone,
        password,
        district,
        category,
        income: parseInt(income),
        age: parseInt(age),
        family_size: parseInt(family_size),
        language: signupData.language
      });
      
      if (result.success) {
        await login(phone, password);
      } else {
        setSignupError(result.errors?.join(', ') || 'Registration failed');
      }
    } finally {
      setIsSignupLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full font-body absolute inset-0 z-50 bg-base">
      {/* Left Decorative Panel */}
      <div className="hidden lg:flex flex-col w-[55%] relative overflow-hidden bg-gradient-to-br from-[#050e07] to-[#0a1f10] text-[#f0f0ee]">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-[#22c55e]/20 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-[#c9820a]/15 rounded-full blur-[140px]"></div>
        <div className="absolute center top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-[#0ea5e9]/10 rounded-full blur-[100px]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[length:32px_32px] opacity-40 mix-blend-overlay"></div>

        <motion.div 
          initial={{ x: '-100%' }}
          animate={{ x: '100%' }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
          className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-[#22c55e] to-transparent"
        />

        <div className="relative z-10 flex flex-col items-center justify-center h-full p-12">
          <div className="flex flex-col items-center mb-12">
            <div className="w-24 h-24 rounded-full bg-[rgba(255,255,255,0.06)] backdrop-blur-[20px] border border-[rgba(255,255,255,0.12)] flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(34,197,94,0.15)] relative">
              <div className="absolute inset-0 rounded-full border border-[#22c55e]/30 animate-pulse"></div>
              <Building2 size={64} className="text-[#f0f0ee]" strokeWidth={1} />
            </div>
            
            <h1 className="font-display font-bold text-[36px] tracking-tight mb-2">Panchayat Seva Agent</h1>
            <p className="font-malayalam text-[16px] text-white/50 tracking-wider">പഞ്ചായത്ത് സേവ ഏജന്റ്</p>
            
            <div className="mt-8 flex items-center gap-2 bg-black/40 px-4 py-2 rounded-full border border-white/10">
              <div className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse"></div>
              <span className="text-sm font-medium tracking-wide">Sovereign AI · Kerala</span>
            </div>
          </div>

          <div className="flex flex-col gap-4 w-full max-w-[420px]">
            <FeatureCard icon={<Languages />} text="Malayalam & English seamless switching" delay={0.1} />
            <FeatureCard icon={<Bell />} text="Proactive scheme matching & alerts" delay={0.2} ml="4" />
            <FeatureCard icon={<ShieldCheck />} text="Secure, local data storage in India" delay={0.3} ml="8" />
          </div>

          <div className="absolute bottom-8 text-[11px] font-mono text-white/30 tracking-widest uppercase">
            Powered by Sarvam AI · Gemini · LangChain
          </div>
        </div>
      </div>

      {/* Right Auth Panel */}
      <div className="flex-1 flex items-center justify-center bg-base relative overflow-hidden">
        <div className="w-full max-w-[480px] p-8 z-10 relative">
          <AnimatePresence mode="wait">
            {view === 'login' ? (
              <motion.div 
                key="login"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.3 }}
                className="glass p-8 sm:p-10 rounded-[16px]"
              >
                <div className="mb-8">
                  <h2 className="font-display font-bold text-3xl text-primary mb-2">Welcome back</h2>
                  <p className="text-sm text-secondary">Sign in to access your dashboard</p>
                  <div className="h-[2px] w-12 bg-gradient-to-r from-brand to-transparent mt-4 rounded-full"></div>
                </div>

                <div className="space-y-5">
                  <Input 
                    icon={<Smartphone size={18} />}
                    placeholder="Phone number"
                    type="tel"
                    value={loginPhone}
                    onChange={(e) => setLoginPhone(e.target.value)}
                  />
                  <PasswordInput 
                    value={loginPassword}
                    onChange={setLoginPassword}
                  />

                  {loginError && (
                    <p className="text-red-500 text-sm">{loginError}</p>
                  )}

                  <button 
                    onClick={handleLogin}
                    disabled={isLoginLoading}
                    className="w-full flex items-center justify-center gap-2 bg-brand hover:bg-brand/90 hover:shadow-[0_0_15px_rgba(10,86,53,0.4)] text-[#f0f0ee] transition-all duration-300 py-3 rounded-[10px] font-medium mt-6 disabled:opacity-50"
                  >
                    {isLoginLoading ? <Loader2 size={18} className="animate-spin" /> : 'Sign in'}
                    {!isLoginLoading && <ArrowRight size={18} />}
                  </button>

                  <div className="mt-6 text-center text-sm text-muted">
                    Don't have an account?{' '}
                    <button onClick={() => setView('signup')} className="text-brand hover:text-accent font-medium transition-colors">
                      Create one &rarr;
                    </button>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="signup"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.3 }}
                className="glass p-6 sm:p-8 rounded-[16px] max-h-[95vh] overflow-y-auto custom-scroll"
              >
                <div className="mb-4">
                  <h2 className="font-display font-bold text-2xl text-primary mb-1">Create your account</h2>
                  <p className="text-sm text-secondary">We'll match you with schemes you qualify for</p>
                </div>

                <div className="space-y-3">
                  <div className="relative pl-6 border-l-2 border-brand/30 pb-2">
                    <div className="absolute -left-[14px] -top-1 p-1.5 bg-base rounded-full border border-subtle">
                      <User size={16} className="text-brand" />
                    </div>
                    <div className="space-y-4 pt-1">
                      <Input 
                        icon={<User size={18} />} 
                        placeholder="Your full name"
                        value={signupData.name}
                        onChange={(e) => setSignupData({...signupData, name: e.target.value})}
                      />
                      <div>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Smartphone size={18} className="text-muted" />
                          </div>
                          <div className="absolute inset-y-0 left-10 flex items-center">
                            <span className="text-sm font-medium bg-brand/10 text-brand px-1.5 py-0.5 rounded">+91</span>
                          </div>
                          <input 
                            type="tel" 
                            className="w-full bg-panel border border-default rounded-[10px] pl-[84px] pr-4 py-2 text-sm text-primary placeholder:text-muted focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand/50 transition-all font-body"
                            placeholder="98765 43210"
                            value={signupData.phone}
                            onChange={(e) => setSignupData({...signupData, phone: e.target.value})}
                          />
                        </div>
                      </div>
                      <Input 
                        icon={<Lock size={18} />} 
                        placeholder="Password"
                        type="password"
                        value={signupData.password}
                        onChange={(e) => setSignupData({...signupData, password: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="relative pl-6 border-l-2 border-brand/30 pb-2">
                    <div className="absolute -left-[14px] -top-1 p-1.5 bg-base rounded-full border border-subtle">
                      <MapPin size={16} className="text-brand" />
                    </div>
                    <div className="space-y-2 pt-1 flex gap-3">
                      <select 
                        className="w-1/2 bg-panel border border-default rounded-[10px] px-3 py-2 text-sm text-primary focus:border-brand outline-none cursor-pointer appearance-none"
                        value={signupData.district}
                        onChange={(e) => setSignupData({...signupData, district: e.target.value})}
                      >
                        <option value="">District</option>
                        {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                      <select 
                        className="w-1/2 bg-panel border border-default rounded-[10px] px-3 py-2 text-sm text-primary focus:border-brand outline-none cursor-pointer appearance-none"
                        value={signupData.category}
                        onChange={(e) => setSignupData({...signupData, category: e.target.value})}
                      >
                        <option value="">Category</option>
                        {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="relative pl-6 border-l-2 border-brand/30">
                    <div className="absolute -left-[14px] -top-1 p-1.5 bg-base rounded-full border border-subtle">
                      <BarChart2 size={16} className="text-brand" />
                    </div>
                    <div className="space-y-2 pt-1">
                      <Input 
                        icon={<IndianRupee size={18} />} 
                        placeholder="Annual Income (e.g. 150000)"
                        type="number"
                        value={signupData.income}
                        onChange={(e) => setSignupData({...signupData, income: e.target.value})}
                      />
                      
                      <div className="flex gap-3">
                        <Input 
                          icon={<Calendar size={18} />} 
                          placeholder="Age"
                          type="number"
                          value={signupData.age}
                          onChange={(e) => setSignupData({...signupData, age: e.target.value})}
                        />
                        <div className="flex items-center bg-panel border border-default rounded-[10px] px-3">
                          <Users size={18} className="text-muted mr-2" />
                          <input 
                            type="number" 
                            min="1" 
                            max="20" 
                            placeholder="Family"
                            className="w-full bg-transparent text-sm border-none outline-none text-primary py-2"
                            value={signupData.family_size}
                            onChange={(e) => setSignupData({...signupData, family_size: e.target.value})}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="relative pl-6 border-l-2 border-brand/30">
                    <div className="absolute -left-[14px] -top-1 p-1.5 bg-base rounded-full border border-subtle">
                      <Languages size={16} className="text-brand" />
                    </div>
                    <div className="pt-1">
                      <select 
                        className="w-full bg-panel border border-default rounded-[10px] px-3 py-2 text-sm text-primary focus:border-brand outline-none cursor-pointer appearance-none transition-all focus:ring-1 focus:ring-brand/50"
                        value={signupData.language}
                        onChange={(e) => setSignupData({...signupData, language: e.target.value})}
                      >
                        <option value="malayalam">Malayalam (മലയാളം)</option>
                        <option value="english">English</option>
                      </select>
                    </div>
                  </div>

                  {signupError && (
                    <p className="text-red-500 text-sm">{signupError}</p>
                  )}

                  <div className="mt-4 pt-3 border-t border-subtle">
                    <button 
                      onClick={handleSignup}
                      disabled={isSignupLoading}
                      className="w-full flex items-center justify-center gap-2 bg-brand hover:bg-brand/90 hover:-translate-y-0.5 text-[#f0f0ee] transition-all duration-300 py-3 rounded-[10px] font-medium shadow-[0_4px_14px_rgba(10,86,53,0.3)] disabled:opacity-50"
                    >
                      {isSignupLoading ? <Loader2 size={18} className="animate-spin" /> : 'Create account'}
                      {!isSignupLoading && <ArrowRight size={18} />}
                    </button>
                    
                    <p className="text-center text-[10px] text-muted mt-2">
                      By creating an account you agree to our Privacy Policy
                    </p>

                    <div className="mt-2 text-center text-sm text-muted border-t border-default pt-3">
                      Already have an account?{' '}
                      <button onClick={() => setView('login')} className="text-brand hover:underline font-medium">
                        Sign in
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, text, delay, ml = "0" }: { icon: React.ReactNode, text: string, delay: number, ml?: string }) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 + delay, duration: 0.5 }}
      style={{ marginLeft: `${ml}rem` }}
      className="flex items-center gap-4 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] backdrop-blur-[12px] py-3 px-5 rounded-[16px] shadow-[0_8px_32px_rgba(0,0,0,0.2)]"
    >
      <div className="text-[#22c55e] shrink-0">
        {icon}
      </div>
      <p className="text-[14px] font-medium tracking-wide">{text}</p>
    </motion.div>
  );
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon: React.ReactNode;
}

function Input({ icon, ...props }: InputProps) {
  return (
    <div className="relative group">
      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted group-focus-within:text-brand transition-colors">
        {icon}
      </div>
      <input 
        className="w-full bg-panel border border-default rounded-[10px] pl-[40px] pr-4 py-2 text-sm text-primary placeholder:text-muted focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand/50 transition-all font-body shadow-sm"
        {...props}
      />
    </div>
  );
}

function PasswordInput({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [show, setShow] = useState(false);
  
  return (
    <div>
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted group-focus-within:text-brand transition-colors">
          <Lock size={18} />
        </div>
        <input 
          type={show ? "text" : "password"}
          placeholder="Password"
          className="w-full bg-panel border border-default rounded-[10px] pl-[40px] pr-[40px] py-2 text-sm text-primary placeholder:text-muted focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand/50 transition-all font-body shadow-sm"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        <button 
          onClick={() => setShow(!show)}
          type="button"
          className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-muted hover:text-primary transition-colors"
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  );
}
