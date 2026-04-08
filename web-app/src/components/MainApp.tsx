import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, Bell, User, Sun, Moon, LogOut, 
  Search, Trash2, CheckCheck, ChevronLeft, ChevronRight,
  MoreHorizontal, Paperclip, Mic, FileText, ShoppingBag, 
  Building2, Home, PenLine, Send, RefreshCw, X, AlertCircle
} from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext';
import { 
  sendMessage, ChatMessage, getNotifications, markNotificationRead, Notification,
  getAllConversations, getActiveConversation, createConversation, 
  updateConversation, setActiveConversation, deleteConversation,
  Conversation
} from '../services/api';

export default function MainApp({ theme, toggleTheme, onLogout, onShowLanding }: { theme: 'dark' | 'light', toggleTheme: () => void, onLogout: () => void, onShowLanding: () => void }) {
  const { user, eligibleSchemes, refreshSchemes } = useAuth();
  const [sidebarView, setSidebarView] = useState<'chat' | 'notifications' | 'profile'>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const fetchNotifications = useCallback(async () => {
    if (!user?.user_id) return;
    setIsLoadingNotifications(true);
    try {
      const result = await getNotifications(user.user_id);
      if (result.success) {
        setNotifications(result.notifications);
      }
    } catch (e) {
      console.error('Failed to fetch notifications:', e);
    } finally {
      setIsLoadingNotifications(false);
    }
  }, [user?.user_id]);

  const loadConversations = useCallback(() => {
    if (!user?.user_id) return;
    const convs = getAllConversations(user.user_id);
    setConversations(convs);
    
    const active = getActiveConversation(user.user_id);
    if (active) {
      setMessages(active.messages);
      setActiveConvId(active.id);
      setIsFirstMessage(active.messages.length === 0);
    } else {
      setMessages([]);
      setActiveConvId(null);
      setIsFirstMessage(true);
    }
  }, [user?.user_id]);

  useEffect(() => {
    if (user?.user_id) {
      loadConversations();
      fetchNotifications();
    }
  }, [user?.user_id, fetchNotifications, loadConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (user?.user_id && eligibleSchemes.length === 0) {
      refreshSchemes();
    }
  }, [user?.user_id, eligibleSchemes.length, refreshSchemes]);

  const handleMarkNotificationRead = async (notificationId: number) => {
    try {
      await markNotificationRead(notificationId);
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
    } catch (e) {
      console.error('Failed to mark notification read:', e);
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || !user?.user_id || isLoading) return;

    const currentUserId = user.user_id;
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    const wasFirst = isFirstMessage;
    let currentConvId = activeConvId;
    
    // Create new conversation if none exists
    if (!currentConvId) {
      const newConv = createConversation(currentUserId, userMessage.content);
      currentConvId = newConv.id;
      setActiveConvId(currentConvId);
    }
    
    const updatedMessages = [...messages, userMessage];
    
    setMessages(updatedMessages);
    if (currentConvId) {
      updateConversation(currentUserId, currentConvId, updatedMessages, wasFirst ? userMessage.content : '');
    }
    
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const result = await sendMessage(currentUserId, userMessage.content, wasFirst);
      if (wasFirst) setIsFirstMessage(false);
      if (result.success && result.response) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        };
        const finalMessages = [...updatedMessages, assistantMessage];
        setMessages(finalMessages);
        if (currentConvId) {
          updateConversation(currentUserId, currentConvId, finalMessages);
        }
        loadConversations();
      } else {
        setError(result.error || 'Failed to get response');
      }
    } catch (e) {
      setError('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startVoiceInput = useCallback(() => {
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognitionAPI) {
      setSpeechError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      setTimeout(() => setSpeechError(null), 4000);
      setIsSpeechSupported(false);
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognitionRef.current = recognition;
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'ml-IN';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setSpeechError(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setInputValue(transcript);
      if (event.results[event.results.length - 1].isFinal) {
        setIsListening(false);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setIsListening(false);
      if (event.error === 'not-allowed') {
        setSpeechError('Microphone permission denied. Please allow microphone access.');
      } else if (event.error === 'no-speech') {
        setSpeechError('No speech detected. Please try again.');
      } else if (event.error === 'network') {
        setSpeechError('Network error during speech recognition.');
      } else {
        setSpeechError('Speech recognition error. Please try again.');
      }
      setTimeout(() => setSpeechError(null), 4000);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (e) {
      setIsListening(false);
      setSpeechError('Failed to start speech recognition.');
      setTimeout(() => setSpeechError(null), 4000);
    }
  }, [isListening]);

  useEffect(() => {
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSpeechSupported(!!SpeechRecognitionAPI);
    
    return () => {
      recognitionRef.current?.abort();
    };
  }, []);

  const handleSendWithMessage = async (message: string) => {
    if (!message.trim() || !user?.user_id || isLoading) return;

    const currentUserId = user.user_id;
    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    const wasFirst = isFirstMessage;
    let currentConvId = activeConvId;
    
    if (!currentConvId) {
      const newConv = createConversation(currentUserId, userMessage.content);
      currentConvId = newConv.id;
      setActiveConvId(currentConvId);
    }
    
    const updatedMessages = [...messages, userMessage];
    
    setMessages(updatedMessages);
    if (currentConvId) {
      updateConversation(currentUserId, currentConvId, updatedMessages, wasFirst ? userMessage.content : '');
    }
    
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const result = await sendMessage(currentUserId, userMessage.content, wasFirst);
      if (wasFirst) setIsFirstMessage(false);
      if (result.success && result.response) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        };
        const finalMessages = [...updatedMessages, assistantMessage];
        setMessages(finalMessages);
        if (currentConvId) {
          updateConversation(currentUserId, currentConvId, finalMessages);
        }
        loadConversations();
      } else {
        setError(result.error || 'Failed to get response');
      }
    } catch (e) {
      setError('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    if (!user?.user_id) return;
    createConversation(user.user_id, '');
    loadConversations();
    setMessages([]);
    setActiveConvId(null);
    setIsFirstMessage(true);
  };

  const handleSelectConversation = (convId: string) => {
    if (!user?.user_id) return;
    setActiveConversation(user.user_id, convId);
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setMessages(conv.messages);
      setActiveConvId(convId);
      setIsFirstMessage(conv.messages.length === 0);
    }
  };

  const handleDeleteConversation = (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (!user?.user_id) return;
    deleteConversation(user.user_id, convId);
    loadConversations();
    if (activeConvId === convId) {
      const remaining = getAllConversations(user.user_id);
      if (remaining.length > 0) {
        handleSelectConversation(remaining[0].id);
      } else {
        setMessages([]);
        setActiveConvId(null);
        setIsFirstMessage(true);
      }
    }
  };

  const handleClearCurrentChat = () => {
    if (!user?.user_id || !activeConvId) return;
    deleteConversation(user.user_id, activeConvId);
    loadConversations();
    const remaining = getAllConversations(user.user_id);
    if (remaining.length > 0) {
      handleSelectConversation(remaining[0].id);
    } else {
      setMessages([]);
      setActiveConvId(null);
      setIsFirstMessage(true);
    }
  };

  return (
    <div className="flex h-screen w-full bg-base font-body overflow-hidden">
      {/* Panel A - Icon Sidebar */}
      <div className="w-[56px] min-w-[56px] h-full bg-panel border-r border-default flex flex-col items-center py-4 z-20 justify-between">
        <div className="flex flex-col gap-4 w-full px-2">
          <button 
            onClick={onShowLanding}
            className="w-10 h-10 bg-brand rounded-[12px] flex items-center justify-center text-[#f0f0ee] shadow-[0_2px_10px_rgba(10,86,53,0.3)] mb-4 mx-auto group relative cursor-pointer hover:opacity-90 transition-opacity"
            title="Back to Home"
          >
            <Building2 size={24} />
          </button>

          <NavIcon icon={<MessageSquare />} label="Chat" active={sidebarView === 'chat'} onClick={() => { setSidebarView('chat'); setIsSidebarOpen(true); }} />
          <NavIcon icon={<Bell />} label="Alerts" active={sidebarView === 'notifications'} badge={notifications.filter(n => !n.is_read).length || undefined} onClick={() => { setSidebarView('notifications'); setIsSidebarOpen(true); }} />
          <NavIcon icon={<User />} label="Profile" active={sidebarView === 'profile'} onClick={() => { setSidebarView('profile'); setIsSidebarOpen(true); }} />
        </div>

        <div className="flex flex-col gap-4 w-full px-2">
          <NavIcon 
            icon={theme === 'dark' ? <Sun /> : <Moon />} 
            label="Theme" 
            onClick={toggleTheme} 
          />
          <NavIcon icon={<LogOut />} label="Logout" onClick={onLogout} />
        </div>
      </div>

      {/* Panel B - Expanded Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="h-full bg-base border-r border-default flex flex-col z-10 overflow-hidden shrink-0 relative"
          >
            <div className="w-[260px] h-full flex flex-col">
              {sidebarView === 'chat' && (
                <ChatHistoryView 
                  conversations={conversations}
                  activeConvId={activeConvId}
                  onSelect={handleSelectConversation}
                  onNewChat={handleNewChat}
                  onDelete={handleDeleteConversation}
                  onClear={handleClearCurrentChat}
                />
              )}
              {sidebarView === 'notifications' && (
                <NotificationsView 
                  notifications={notifications}
                  isLoading={isLoadingNotifications}
                  onMarkRead={handleMarkNotificationRead}
                  onRefresh={fetchNotifications}
                />
              )}
              {sidebarView === 'profile' && <ProfileView />}
            </div>

            <button 
              onClick={() => setIsSidebarOpen(false)}
              className="absolute bottom-4 right-4 w-8 h-8 flex items-center justify-center bg-surface border border-default rounded-full text-muted hover:text-primary z-30 shadow-sm"
            >
              <ChevronLeft size={16} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {!isSidebarOpen && (
        <button 
          onClick={() => setIsSidebarOpen(true)}
          className="absolute bottom-4 left-[72px] w-8 h-8 flex items-center justify-center bg-surface border border-default rounded-full text-muted hover:text-primary z-30 shadow-sm transition-colors"
        >
          <ChevronRight size={16} />
        </button>
      )}

      {/* Panel C - Main Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-base relative">
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-brand/5 via-transparent to-transparent opacity-50"></div>
        
        {/* Topbar */}
        <div className="h-[56px] border-b border-default bg-surface/50 backdrop-blur-md flex items-center justify-between px-6 z-10 shrink-0">
          <div>
            <h3 className="font-display font-bold text-[15px] cursor-text">Scheme Inquiry</h3>
            <p className="text-[11px] text-muted -mt-0.5">Kerala Government Services</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-[rgba(34,197,94,0.1)] border border-[rgba(34,197,94,0.2)] px-2.5 py-1 rounded-full">
              <div className="w-2 h-2 rounded-full bg-[#22c55e]"></div>
              <span className="text-[11px] font-medium text-[#22c55e] uppercase tracking-wider">Ready</span>
            </div>
            <button className="text-muted hover:text-primary"><MoreHorizontal size={20} /></button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-12 py-8 flex flex-col gap-6 custom-scroll relative z-10">
          {messages.length === 0 && <WelcomeState onQuickAction={handleSendWithMessage} />}
          
          {messages.map((msg, idx) => (
            msg.role === 'user' ? (
              <UserMessage key={idx} text={msg.content} time={msg.timestamp} />
            ) : (
              <AgentMessage key={idx} text={msg.content} time={msg.timestamp} />
            )
          ))}

          {isLoading && (
            <div className="flex gap-4 max-w-[85%] self-start animate-pulse">
               <div className="w-8 h-8 rounded-full bg-brand flex items-center justify-center shrink-0 mt-1 shadow-sm">
                <Building2 size={16} className="text-[#f0f0ee]" />
              </div>
              <div className="glass px-4 py-3 rounded-[16px] rounded-tl-[4px]">
                <div className="flex gap-1.5 h-4 items-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/60 animate-bounce"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/60 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/60 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="text-red-500 text-sm px-4 py-2 bg-red-500/10 rounded-lg">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-surface/80 backdrop-blur-md border-t border-default p-4 shrink-0 z-20">
          <div className="max-w-4xl mx-auto flex flex-col gap-2">
            
            <div className="flex gap-2 mb-1 px-1 overflow-x-auto no-scrollbar pb-1">
              {['Documents needed?', 'Check eligibility', 'Find office'].map(hint => (
                <button 
                  key={hint} 
                  className="text-[12px] font-medium px-3 py-1.5 rounded-full border border-subtle bg-base/50 hover:bg-soft text-secondary hover:text-primary whitespace-nowrap transition-colors"
                  onClick={() => {
                    setInputValue(hint);
                    setTimeout(() => handleSendWithMessage(hint), 100);
                  }}
                >
                  {hint}
                </button>
              ))}
            </div>

            <div className="relative flex items-end gap-2 bg-base/80 backdrop-blur-sm border border-default rounded-[12px] p-2 focus-within:ring-2 focus-within:ring-brand/30 focus-within:border-brand shadow-sm transition-all group">
              <button 
                className="p-2 text-muted hover:text-primary shrink-0 opacity-70 group-focus-within:opacity-100"
                onClick={() => setError('Image attachments are not supported. Please type your question.')}
                title="Images not supported"
              >
                <Paperclip size={20} />
              </button>
              
              <textarea 
                rows={1}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full bg-transparent border-none focus:outline-none resize-none py-2 text-[14.5px] leading-relaxed max-h-[120px]"
                placeholder="Type in Malayalam or English... / മലയാളത്തിൽ ടൈപ്പ് ചെയ്യൂ..."
                disabled={isLoading}
              />
              
              <button 
                onClick={startVoiceInput}
                disabled={!isSpeechSupported}
                className={clsx(
                  "p-2 shrink-0 transition-colors rounded-full",
                  isListening 
                    ? "text-red-500 bg-red-50 dark:bg-red-900/20 animate-pulse shadow-sm" 
                    : isSpeechSupported 
                      ? "text-muted hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20" 
                      : "text-muted/40 cursor-not-allowed"
                )}
                title={isListening ? "Listening... Click to stop" : isSpeechSupported ? "Voice input (Malayalam/English)" : "Speech not supported"}
              >
                {isListening ? (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <Mic size={20} />
                  </motion.div>
                ) : (
                  <Mic size={20} />
                )}
              </button>
              
              <button 
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="w-10 h-10 bg-brand hover:bg-brand/90 disabled:opacity-50 disabled:cursor-not-allowed rounded-full flex items-center justify-center text-[#f0f0ee] shrink-0 transition-all shadow-md"
              >
                <Send size={20} />
              </button>
            </div>
            <div className="text-center mt-1 text-[10.5px] text-muted font-medium">
              AI can make mistakes. Please verify important government information.
            </div>
          </div>
        </div>

        {/* Speech Error Toast */}
        <AnimatePresence>
          {speechError && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 max-w-sm w-full px-4"
            >
              <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3 shadow-lg flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/50 flex items-center justify-center shrink-0">
                  <Mic size={16} className="text-red-500" />
                </div>
                <p className="text-sm text-red-700 dark:text-red-300 flex-1">{speechError}</p>
                <button 
                  onClick={() => setSpeechError(null)}
                  className="p-1 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-full transition-colors"
                >
                  <X size={16} className="text-red-400" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Listening Indicator */}
        <AnimatePresence>
          {isListening && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="fixed bottom-28 left-1/2 -translate-x-1/2 z-50"
            >
              <div className="bg-brand text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                  className="w-2 h-2 rounded-full bg-white"
                />
                <span className="text-sm font-medium">Listening...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function WelcomeState({ onQuickAction }: { onQuickAction: (message: string) => void }) {
  const quickActions = [
    { icon: <FileText size={18}/>, label: 'Birth Certificate', msg: 'How to apply for birth certificate?' },
    { icon: <ShoppingBag size={18}/>, label: 'Ration Card', msg: 'How to apply for ration card?' },
    { icon: <Home size={18}/>, label: 'Housing Scheme', msg: 'What housing schemes am I eligible for?' },
    { icon: <Building2 size={18}/>, label: 'Business License', msg: 'How to get a business license?' },
    { icon: <User size={18}/>, label: 'Pension Info', msg: 'What pension schemes am I eligible for?' },
    { icon: <PenLine size={18}/>, label: 'Draft Form', msg: 'Help me draft an application form' },
  ];

  return (
    <div className="flex flex-col items-center justify-center my-auto py-12 text-center max-w-2xl mx-auto w-full">
      <div className="bg-brand/10 text-brand border border-brand/20 px-3 py-1 rounded-full text-xs font-semibold tracking-wide uppercase mb-6 flex items-center gap-1.5 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-brand"></span>
        Sovereign AI · Kerala
      </div>
      
      <h2 className="font-display font-bold text-3xl md:text-4xl text-primary tracking-tight mb-2">How can I help you?</h2>
      <p className="font-malayalam text-lg text-secondary mb-3">നിങ്ങൾക്ക് എന്ത് സഹായമാണ് വേണ്ടത്?</p>
      <p className="text-sm text-muted mb-10 max-w-lg">I can help you find government schemes, check your eligibility, locate offices, and draft applications.</p>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 w-full">
        {quickActions.map(action => (
          <HomeChip 
            key={action.label}
            icon={action.icon} 
            label={action.label}
            onClick={() => onQuickAction(action.msg)}
          />
        ))}
      </div>
    </div>
  );
}

function HomeChip({ icon, label, onClick }: { icon: React.ReactNode, label: string, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className="glass flex items-center gap-3 px-4 py-3 rounded-xl hover:border-brand/40 hover:bg-soft/30 hover:-translate-y-[1px] transition-all group shadow-sm text-left"
    >
      <div className="text-brand opacity-80 group-hover:opacity-100 transition-opacity">
        {icon}
      </div>
      <span className="text-sm font-medium text-secondary group-hover:text-primary">{label}</span>
    </button>
  );
}

function UserMessage({ text, time }: { text: string, time: string }) {
  return (
    <div className="flex flex-col items-end w-full max-w-[85%] self-end">
      <div className="bg-brand text-[#f0f0ee] px-5 py-3 rounded-[16px] rounded-tr-[4px] shadow-[0_2px_12px_rgba(10,86,53,0.25)]">
        <p className="text-[14.5px] leading-relaxed">{text}</p>
      </div>
      <span className="text-[10px] font-mono text-muted mt-1.5 mr-1">{time}</span>
    </div>
  );
}

function AgentMessage({ text, time }: { text: string, time: string }) {
  return (
    <div className="flex gap-4 max-w-[90%] self-start group">
      <div className="w-8 h-8 rounded-full bg-brand flex items-center justify-center shrink-0 mt-1 shadow-sm">
        <Building2 size={16} className="text-[#f0f0ee]" />
      </div>
      <div className="flex flex-col">
        <div className="glass px-5 py-3 rounded-[16px] rounded-tl-[4px]">
          <p className="text-[14.5px] leading-relaxed whitespace-pre-wrap">{text}</p>
        </div>
        <span className="text-[10px] font-mono text-muted mt-1.5 ml-1">{time}</span>
      </div>
    </div>
  );
}

function NavIcon({ icon, label, active, onClick, badge }: any) {
  return (
    <div className="relative group w-full flex justify-center">
      <button 
        onClick={onClick}
        className={clsx(
          "w-[40px] h-[40px] rounded-[12px] flex items-center justify-center transition-all duration-200 cursor-pointer relative",
          active ? "bg-brand text-[#f0f0ee] shadow-md" : "text-muted hover:bg-surface hover:text-primary"
        )}
      >
        {React.cloneElement(icon, { size: 20 })}
        {badge && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-alert rounded-full border-2 border-panel text-[9px] font-bold text-white flex items-center justify-center">
            {badge > 9 ? '9+' : badge}
          </span>
        )}
      </button>
      <div className="absolute left-[calc(100%+8px)] top-1/2 -translate-y-1/2 px-2 py-1 bg-surface border border-default backdrop-blur-md rounded-md text-[12px] font-medium opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-sm whitespace-nowrap">
        {label}
      </div>
    </div>
  );
}

function ChatHistoryView({ 
  conversations, 
  activeConvId, 
  onSelect, 
  onNewChat, 
  onDelete, 
  onClear 
}: { 
  conversations: Conversation[]; 
  activeConvId: string | null;
  onSelect: (id: string) => void; 
  onNewChat: () => void; 
  onDelete: (e: React.MouseEvent, id: string) => void;
  onClear: () => void;
}) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-default flex items-center justify-between shrink-0">
        <h3 className="font-display font-semibold text-sm">Conversations</h3>
        <div className="flex gap-2">
          <button onClick={onNewChat} className="text-muted hover:text-primary" title="New chat">
            <PenLine size={16} />
          </button>
          {activeConvId && (
            <button onClick={onClear} className="text-muted hover:text-red-500" title="Clear current chat">
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>
      <div className="p-3 shrink-0">
        <div className="relative flex items-center bg-surface border border-default rounded-lg px-3 py-1.5">
          <Search size={14} className="text-muted mr-2" />
          <input type="text" placeholder="Search chats..." className="bg-transparent border-none focus:outline-none text-[12px] w-full" />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto custom-scroll px-3 py-2">
        {conversations.length > 0 ? (
          <div className="space-y-1">
            {conversations.map(conv => (
              <div 
                key={conv.id}
                onClick={() => onSelect(conv.id)}
                className={clsx(
                  "px-3 py-2.5 rounded-lg cursor-pointer transition-all group relative",
                  activeConvId === conv.id 
                    ? "border-l-2 border-brand bg-soft" 
                    : "hover:bg-surface border-l-2 border-transparent"
                )}
              >
                <p className={clsx(
                  "text-[13px] truncate font-medium pr-6",
                  activeConvId === conv.id ? "text-primary" : "text-secondary"
                )}>
                  {conv.title || 'New conversation'}
                </p>
                <p className="text-[10px] font-mono text-muted mt-0.5">
                  {formatTime(conv.updatedAt)} · {conv.messages.length} msg
                </p>
                <button 
                  onClick={(e) => onDelete(e, conv.id)}
                  className="absolute top-2 right-2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500 transition-opacity"
                  title="Delete conversation"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted text-sm">
            <p>No conversations yet</p>
            <p className="text-xs mt-1">Start by sending a message</p>
          </div>
        )}
      </div>
    </div>
  );
}

interface NotificationsViewProps {
  notifications: Notification[];
  isLoading: boolean;
  onMarkRead: (id: number) => void;
  onRefresh: () => void;
}

function NotificationsView({ notifications, isLoading, onMarkRead, onRefresh }: NotificationsViewProps) {
  const unreadCount = notifications.filter(n => !n.is_read).length;

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    if (hours < 24) return `${hours} hours ago`;
    if (days === 1) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <div className="flex flex-col h-full bg-base">
      <div className="p-4 border-b border-default shrink-0 flex items-center justify-between">
        <h3 className="font-display font-semibold text-sm">Scheme Alerts</h3>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <div className="bg-alert text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{unreadCount} New</div>
          )}
          <button onClick={onRefresh} className="text-muted hover:text-primary" title="Refresh">
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto custom-scroll p-3 space-y-3">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw size={20} className="animate-spin text-brand" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-8 text-muted">
            <Bell size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No notifications yet</p>
            <p className="text-xs mt-1">We'll notify you when new schemes match your profile</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <NotificationCard 
              key={notification.id}
              notification={notification}
              formatTime={formatTime}
              onMarkRead={onMarkRead}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface NotificationCardProps {
  notification: Notification;
  formatTime: (date: string) => string;
  onMarkRead: (id: number) => void;
}

function NotificationCard({ notification, formatTime, onMarkRead }: NotificationCardProps) {
  const desc = notification.message_ml || notification.message_en || notification.scheme_name;
  
  return (
    <div 
      className={clsx(
        "relative p-3 rounded-xl border bg-surface/50 transition-all cursor-pointer hover:shadow-sm",
        !notification.is_read ? "border-alert/50 border-l-2 border-l-alert" : "border-default"
      )}
      onClick={() => !notification.is_read && onMarkRead(notification.id)}
    >
      {!notification.is_read && <div className="absolute top-3 right-3 w-2 h-2 bg-alert rounded-full"></div>}
      <h4 className={clsx("text-[13px] pr-4", !notification.is_read ? "font-bold text-primary" : "font-medium text-secondary")}>
        {notification.scheme_name}
      </h4>
      <p className="text-[11px] text-muted leading-tight mt-1 mb-2 line-clamp-2">{desc}</p>
      <div className="flex justify-between items-center">
        <span className="text-[10px] font-mono text-muted/70">{formatTime(notification.created_at)}</span>
        {!notification.is_read && (
          <button 
            className="text-brand hover:text-brand/80"
            onClick={(e) => { e.stopPropagation(); onMarkRead(notification.id); }}
          >
            <CheckCheck size={14} />
          </button>
        )}
      </div>
    </div>
  );
}

function ToggleRow({ label, value, onChange }: { label: string, value: boolean, onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-[13px] text-secondary font-medium">{label}</span>
      <button 
        onClick={() => onChange(!value)}
        className={clsx(
          "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none",
          value ? "bg-brand" : "bg-muted/30"
        )}
      >
        <span
          className={clsx(
            "pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
            value ? "translate-x-4" : "translate-x-0"
          )}
        />
      </button>
    </div>
  );
}

function ProfileView() {
  const { user, eligibleSchemes, missingFields, updateProfile, answerMissingField } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<{
    name: string;
    age: number;
    family_size: number;
    language: string;
    gender: 'male' | 'female' | 'other';
    employment_status: 'employed' | 'unemployed' | 'self_employed' | 'govt_employee';
    marital_status: 'married' | 'unmarried' | 'widowed' | 'divorced';
    education_level: 'primary' | 'secondary' | 'higher_secondary' | 'graduate' | 'post_graduate';
    occupation: string;
    house_ownership: 'owned' | 'rented' | 'shelter' | 'none';
    vehicle_type: 'none' | 'two_wheeler' | 'four_wheeler' | 'both';
    has_health_insurance: boolean;
    has_life_insurance: boolean;
    is_urban: boolean;
  }>({ 
    name: '', age: 0, family_size: 0, language: 'english',
    gender: 'male',
    employment_status: 'unemployed',
    marital_status: 'unmarried',
    education_level: 'secondary',
    occupation: '',
    house_ownership: 'owned',
    vehicle_type: 'none',
    has_health_insurance: false,
    has_life_insurance: false,
    is_urban: false
  });
  const [isSaving, setIsSaving] = useState(false);
  const [showMissingFields, setShowMissingFields] = useState(false);
  const [answeringField, setAnsweringField] = useState<string | null>(null);
  
  if (!user) return null;

  const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  const incomeDisplay = user.income >= 100000 ? `₹${(user.income / 100000).toFixed(1)}L` : `₹${user.income}K`;

  const handleEditClick = () => {
    setEditForm({
      name: user.name,
      age: user.age,
      family_size: user.family_size,
      language: user.language,
      gender: user.gender || 'male',
      employment_status: user.employment_status || 'unemployed',
      marital_status: user.marital_status || 'unmarried',
      education_level: user.education_level || 'secondary',
      occupation: user.occupation || '',
      house_ownership: user.house_ownership || 'owned',
      vehicle_type: user.vehicle_type || 'none',
      has_health_insurance: user.has_health_insurance || false,
      has_life_insurance: user.has_life_insurance || false,
      is_urban: user.is_urban || false
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    const result = await updateProfile({
      name: editForm.name,
      age: editForm.age,
      family_size: editForm.family_size,
      language: editForm.language,
      gender: editForm.gender,
      employment_status: editForm.employment_status,
      marital_status: editForm.marital_status,
      education_level: editForm.education_level,
      occupation: editForm.occupation,
      house_ownership: editForm.house_ownership,
      vehicle_type: editForm.vehicle_type,
      has_health_insurance: editForm.has_health_insurance,
      has_life_insurance: editForm.has_life_insurance,
      is_urban: editForm.is_urban
    });
    setIsSaving(false);
    if (result.success) {
      setIsEditing(false);
    }
  };

  const handleAnswerField = async (field: string, value: string, inputType: string) => {
    if (inputType === 'yesno') {
      const boolValue = value === 'yes' ? 'Yes' : 'No';
      const success = await answerMissingField(field, boolValue);
      if (success) {
        setAnsweringField(null);
      }
    }
  };

  if (isEditing) {
    return (
      <div className="flex flex-col h-full bg-base">
        <div className="p-4 border-b border-default shrink-0 flex items-center justify-between bg-panel">
          <h3 className="font-display font-semibold text-sm">Edit Profile</h3>
          <button onClick={() => setIsEditing(false)} className="text-muted hover:text-primary"><X size={16}/></button>
        </div>
        <div className="flex-1 overflow-y-auto custom-scroll p-4 space-y-6">
          {/* Section: Basic Information */}
          <div className="space-y-4">
            <h4 className="text-[10px] uppercase tracking-[0.2em] text-brand font-bold mb-3">Basic Information</h4>
            <div>
              <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Name</label>
              <input
                type="text"
                value={editForm.name}
                onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
                className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors"
                placeholder="Full Name"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Age</label>
                <input
                  type="number"
                  value={editForm.age}
                  onChange={e => setEditForm(f => ({ ...f, age: parseInt(e.target.value) || 0 }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors"
                />
              </div>
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Gender</label>
                <select
                  value={editForm.gender}
                  onChange={e => setEditForm(f => ({ ...f, gender: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Marital Status</label>
                <select
                  value={editForm.marital_status}
                  onChange={e => setEditForm(f => ({ ...f, marital_status: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="unmarried">Unmarried</option>
                  <option value="married">Married</option>
                  <option value="widowed">Widowed</option>
                  <option value="divorced">Divorced</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Language</label>
                <select
                  value={editForm.language}
                  onChange={e => setEditForm(f => ({ ...f, language: e.target.value }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="english">English</option>
                  <option value="malayalam">Malayalam</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section: Socio-Economic */}
          <div className="space-y-4">
            <h4 className="text-[10px] uppercase tracking-[0.2em] text-brand font-bold mb-3">Socio-Economic</h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Education</label>
                <select
                  value={editForm.education_level}
                  onChange={e => setEditForm(f => ({ ...f, education_level: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="primary">Primary</option>
                  <option value="secondary">Secondary</option>
                  <option value="higher_secondary">Higher Secondary</option>
                  <option value="graduate">Graduate</option>
                  <option value="post_graduate">Post Graduate</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Employment</label>
                <select
                  value={editForm.employment_status}
                  onChange={e => setEditForm(f => ({ ...f, employment_status: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="employed">Employed</option>
                  <option value="unemployed">Unemployed</option>
                  <option value="self_employed">Self Employed</option>
                  <option value="govt_employee">Govt Employee</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Occupation</label>
              <input
                type="text"
                value={editForm.occupation}
                onChange={e => setEditForm(f => ({ ...f, occupation: e.target.value }))}
                className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors"
                placeholder="Ex: Farmer, Teacher, etc."
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Family Size</label>
                <input
                  type="number"
                  value={editForm.family_size}
                  onChange={e => setEditForm(f => ({ ...f, family_size: parseInt(e.target.value) || 0 }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors"
                />
              </div>
            </div>
          </div>

          {/* Section: Life & Household */}
          <div className="space-y-4">
            <h4 className="text-[10px] uppercase tracking-[0.2em] text-brand font-bold mb-3">Life & Household</h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">House</label>
                <select
                  value={editForm.house_ownership}
                  onChange={e => setEditForm(f => ({ ...f, house_ownership: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="owned">Owned</option>
                  <option value="rented">Rented</option>
                  <option value="shelter">Shelter</option>
                  <option value="none">None</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] font-medium text-muted uppercase tracking-wide">Vehicle</label>
                <select
                  value={editForm.vehicle_type}
                  onChange={e => setEditForm(f => ({ ...f, vehicle_type: e.target.value as any }))}
                  className="w-full mt-1 px-3 py-2 border border-default rounded-lg text-sm bg-panel focus:outline-none focus:border-brand transition-colors appearance-none cursor-pointer"
                >
                  <option value="none">None</option>
                  <option value="two_wheeler">Two Wheeler</option>
                  <option value="four_wheeler">Four Wheeler</option>
                  <option value="both">Both</option>
                </select>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <ToggleRow 
                label="Health Insurance" 
                value={editForm.has_health_insurance} 
                onChange={v => setEditForm(f => ({ ...f, has_health_insurance: v }))} 
              />
              <ToggleRow 
                label="Life Insurance" 
                value={editForm.has_life_insurance} 
                onChange={v => setEditForm(f => ({ ...f, has_life_insurance: v }))} 
              />
              <ToggleRow 
                label="Urban Resident" 
                value={editForm.is_urban} 
                onChange={v => setEditForm(f => ({ ...f, is_urban: v }))} 
              />
            </div>
          </div>
        </div>
        
        <div className="p-4 bg-panel border-t border-default shrink-0 flex gap-3">
          <button
            onClick={() => setIsEditing(false)}
            className="flex-1 py-2.5 border border-default rounded-lg text-[13px] font-medium hover:bg-surface transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 py-2.5 bg-brand text-white rounded-lg text-[13px] font-medium hover:opacity-90 transition-opacity disabled:opacity-50 shadow-md"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-default shrink-0">
        <h3 className="font-display font-semibold text-sm">Profile Details</h3>
      </div>
      <div className="p-4 flex flex-col items-center border-b border-default">
        <div className="w-16 h-16 rounded-full bg-brand flex items-center justify-center text-white font-display font-bold text-xl mb-3 shadow-md">
          {initials}
        </div>
        <h4 className="font-display font-bold text-[15px]">{user.name}</h4>
        <p className="text-[12px] text-muted">{user.district} · {user.category}</p>
      </div>
      
      <div className="p-4 flex-1 overflow-y-auto custom-scroll">
        <div className="grid grid-cols-2 gap-2 mb-4">
          <MetricCard label="Income" value={incomeDisplay} />
          <MetricCard label="Age" value={user.age.toString()} />
          <MetricCard label="Family" value={user.family_size.toString()} />
          <MetricCard label="Language" value={user.language === 'malayalam' ? 'Malayalam' : 'English'} />
        </div>
        
        {missingFields.length > 0 && (
          <div className="mb-4">
            <button
              onClick={() => setShowMissingFields(!showMissingFields)}
              className="w-full py-3 px-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-center gap-2 text-left hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
            >
              <AlertCircle size={18} className="text-amber-500 shrink-0" />
              <div className="flex-1">
                <p className="text-[13px] font-medium text-amber-700 dark:text-amber-400">
                  Profile Incomplete ({missingFields.length} missing)
                </p>
                <p className="text-[11px] text-amber-600 dark:text-amber-500">
                  Tap to answer eligibility questions
                </p>
              </div>
            </button>
            
            <AnimatePresence>
              {showMissingFields && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden mt-2 space-y-2"
                >
                  {missingFields.slice(0, 5).map((field, idx) => (
                    <div key={idx} className="bg-surface border border-default rounded-lg p-3">
                      <p className="text-[12px] font-medium text-primary mb-1">
                        {user.language === 'malayalam' ? field.question_ml : field.question_en}
                      </p>
                      <p className="text-[10px] text-muted mb-2">
                        For: {field.scheme}
                      </p>
                      {answeringField === field.field ? (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleAnswerField(field.field, 'yes', field.input_type)}
                            className="flex-1 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg text-[12px] font-medium hover:bg-green-200 dark:hover:bg-green-900/50"
                          >
                            അതെ / Yes
                          </button>
                          <button
                            onClick={() => handleAnswerField(field.field, 'no', field.input_type)}
                            className="flex-1 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg text-[12px] font-medium hover:bg-red-200 dark:hover:bg-red-900/50"
                          >
                            അല്ല / No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setAnsweringField(field.field)}
                          className="w-full py-1.5 bg-brand/10 text-brand rounded-lg text-[12px] font-medium hover:bg-brand/20"
                        >
                          Answer
                        </button>
                      )}
                    </div>
                  ))}
                  {missingFields.length > 5 && (
                    <p className="text-[11px] text-muted text-center">
                      +{missingFields.length - 5} more questions
                    </p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
        
        <button 
          onClick={handleEditClick}
          className="w-full py-2 border flex items-center justify-center border-default rounded-lg text-[13px] font-medium hover:bg-surface transition-colors mb-4 text-primary"
        >
          Edit Profile
        </button>

        <h5 className="text-[12px] font-bold uppercase tracking-wider text-muted mb-3">Top Matches</h5>
        <div className="space-y-2">
          {eligibleSchemes.slice(0, 5).map((scheme, idx) => (
            <div key={idx} className="glass px-3 py-2 rounded-lg flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-brand shrink-0"></div>
              <span className="text-[12px] font-medium truncate">{scheme.scheme_name}</span>
            </div>
          ))}
          {eligibleSchemes.length === 0 && (
            <p className="text-sm text-muted">Complete your profile to see matches</p>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string, value: string }) {
  return (
    <div className="bg-surface border border-default p-2 rounded-lg text-center">
      <p className="text-[10px] text-muted uppercase tracking-wide mb-0.5">{label}</p>
      <p className="text-[13px] font-semibold text-primary">{value}</p>
    </div>
  );
}
