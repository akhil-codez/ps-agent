import { motion } from 'framer-motion';
import { ArrowRight, FileText, Globe, ShieldCheck, Sun, Moon } from 'lucide-react';

const FloatingParticles = () => {
  // Generate pseudo-random arrays outside render loop to prevent React recreation on resize
  const particles = Array.from({ length: 30 }).map((_, i) => ({
    id: i,
    size: Math.random() * 5 + 1,
    initialX: Math.random() * 100,
    initialY: Math.random() * 100,
    xDrift: (Math.random() - 0.5) * 150,
    yDrift: -150 - Math.random() * 200,
    duration: Math.random() * 15 + 15,
    delay: Math.random() * -20 // start midway randomly
  }));

  return (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-[#22c55e] shadow-[0_0_12px_rgba(34,197,94,0.4)]"
          style={{
            width: p.size,
            height: p.size,
            left: `${p.initialX}%`,
            top: `${p.initialY}%`,
          }}
          animate={{
            y: [0, p.yDrift],
            x: [0, p.xDrift],
            opacity: [0, 0.8, 0],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            ease: "linear",
            delay: p.delay,
          }}
        />
      ))}
    </div>
  );
};

export default function LandingScreen({ onShowAuth, theme, toggleTheme }: { onShowAuth: () => void, theme: 'dark' | 'light', toggleTheme: () => void }) {
  // Staggered animation configurations
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.2 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  // Landing screen is visible only when not logged in
  // The actual navigation is handled by App.tsx with AuthContext

  return (
    <div className="relative min-h-screen w-full flex flex-col overflow-hidden bg-base text-primary">
      {/* Background Ambient Orbs & Particles */}
      <FloatingParticles />
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-brand/20 blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-accent/10 blur-[150px]" />

      {/* Top Navbar / Header area */}
      <nav className="w-full relative z-20 flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="flex flex-col">
          <span className="font-display font-bold text-lg tracking-tight">Panchayat Seva</span>
          <span className="text-[10px] uppercase tracking-[0.2em] text-accent font-medium">Sovereign AI · Kerala</span>
        </div>
        <button 
          onClick={onShowAuth}
          className="text-sm font-medium px-5 py-2.5 rounded-full border border-default hover:bg-surface transition-colors cursor-pointer"
        >
          Sign In
        </button>
      </nav>

      {/* Main Hero Content */}
      <main className="flex-1 w-full relative z-10 flex flex-col items-center justify-center -mt-16 px-6 pb-32">
        <motion.div 
          className="max-w-4xl w-full text-center flex flex-col items-center"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          {/* Badge */}
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-brand/30 bg-brand/10 mb-32 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-xs font-semibold text-accent tracking-wide uppercase">Pilot Active</span>
          </motion.div>

          <motion.h1 variants={itemVariants} className="font-display font-extrabold text-5xl md:text-7xl tracking-tighter leading-[1.05] mb-4">
            Simplify your <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-accent to-brand">
              Panchayat Services
            </span>
          </motion.h1>

          <motion.h2 variants={itemVariants} className="font-malayalam text-xl md:text-2xl text-brand font-semibold mb-8">
            പഞ്ചായത്ത് സേവനങ്ങൾ ഇനി കൂടുതൽ വേഗത്തിൽ
          </motion.h2>

          <motion.p variants={itemVariants} className="text-lg md:text-xl text-secondary max-w-2xl mb-10 leading-relaxed font-body">
            Experience next-generation governance wrapped in an intuitive AI assistant. Localized in Malayalam, built with security, and designed for you.
          </motion.p>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-4">
            <button 
              onClick={onShowAuth}
              className="group relative cursor-pointer flex items-center justify-center gap-2 px-8 py-4 bg-brand text-white font-medium rounded-full overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(34,197,94,0.3)]"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:animate-[shimmer_1.5s_infinite]" />
              <span className="relative z-10">Get Started Now</span>
              <ArrowRight size={18} className="relative z-10 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>

          {/* Feature highlights below Hero */}
          <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 max-w-5xl w-full">
            <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-surface/50 border border-default backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-brand/10 flex items-center justify-center mb-4 text-brand">
                <Globe size={24} />
              </div>
              <h3 className="font-display font-semibold mb-2">Native Malayalam</h3>
              <p className="text-sm text-secondary">A highly localized model for perfect regional tongue synthesis.</p>
            </div>
            
            <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-surface/50 border border-default backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-brand/10 flex items-center justify-center mb-4 text-brand">
                <ShieldCheck size={24} />
              </div>
              <h3 className="font-display font-semibold mb-2">Air-gapped Security</h3>
              <p className="text-sm text-secondary">Private context windows ensure your data never leaves local boundaries.</p>
            </div>

            <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-surface/50 border border-default backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-brand/10 flex items-center justify-center mb-4 text-brand">
                <FileText size={24} />
              </div>
              <h3 className="font-display font-semibold mb-2">Proactive Alerts</h3>
              <p className="text-sm text-secondary">Real-time matching of government schemes sent straight to your WhatsApp.</p>
            </div>
          </motion.div>

        </motion.div>
      </main>

      {/* Theme Toggle Floating Button */}
      <button 
        onClick={toggleTheme}
        className="absolute bottom-6 right-6 w-10 h-10 rounded-full bg-surface border border-default flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-all text-secondary hover:text-primary z-50 cursor-pointer backdrop-blur-md"
        title="Toggle Theme"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

    </div>
  );
}
