import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { UserProfile, login as apiLogin, getProfile as apiGetProfile, updateProfile as apiUpdateProfile, getEligibleSchemes as apiGetEligibleSchemes, getMissingEligibilityFields, saveEligibilityAnswer, Scheme, MissingField } from '../services/api';

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  eligibleSchemes: Scheme[];
  missingFields: MissingField[];
  login: (phone: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  updateProfile: (updates: Partial<UserProfile>) => Promise<{ success: boolean; error?: string }>;
  refreshSchemes: () => Promise<void>;
  refreshMissingFields: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  answerMissingField: (field: string, value: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [eligibleSchemes, setEligibleSchemes] = useState<Scheme[]>([]);
  const [missingFields, setMissingFields] = useState<MissingField[]>([]);

  useEffect(() => {
    const savedUser = localStorage.getItem('ps_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('ps_user');
      }
    }
  }, []);

  useEffect(() => {
    if (user) {
      localStorage.setItem('ps_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('ps_user');
    }
  }, [user]);

  const refreshProfile = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const result = await apiGetProfile(user.user_id);
      if (result.success && result.profile) {
        setUser(result.profile);
      }
    } catch (e) {
      console.error('Failed to refresh profile:', e);
    }
  }, [user?.user_id]);

  const refreshSchemes = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const result = await apiGetEligibleSchemes(user.user_id);
      if (result.success) {
        setEligibleSchemes(result.eligible_schemes);
      }
    } catch (e) {
      console.error('Failed to refresh schemes:', e);
    }
  }, [user?.user_id]);

  const refreshMissingFields = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const result = await getMissingEligibilityFields(user.user_id);
      if (result.success) {
        setMissingFields(result.missing_fields);
      }
    } catch (e) {
      console.error('Failed to refresh missing fields:', e);
    }
  }, [user?.user_id]);

  const answerMissingField = useCallback(async (field: string, value: string): Promise<boolean> => {
    if (!user?.user_id) return false;
    try {
      const result = await saveEligibilityAnswer(user.user_id, field, value);
      if (result.success) {
        await refreshMissingFields();
        await refreshSchemes();
        return true;
      }
      return false;
    } catch (e) {
      console.error('Failed to save answer:', e);
      return false;
    }
  }, [user?.user_id, refreshMissingFields, refreshSchemes]);

  const login = useCallback(async (phone: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiLogin(phone, password);
      if (result.success && result.profile) {
        setUser(result.profile);
        setError(null);
        
        setTimeout(() => {
          refreshSchemes();
          refreshMissingFields();
        }, 100);
        
        return { success: true };
      } else {
        const errMsg = result.error || 'Login failed';
        setError(errMsg);
        return { success: false, error: errMsg };
      }
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : 'Network error. Please try again.';
      setError(errMsg);
      return { success: false, error: errMsg };
    } finally {
      setIsLoading(false);
    }
  }, [refreshSchemes, refreshMissingFields]);

  const logout = useCallback(() => {
    setUser(null);
    setEligibleSchemes([]);
    setMissingFields([]);
    setError(null);
    localStorage.removeItem('ps_user');
  }, []);

  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    if (!user?.user_id) return { success: false, error: 'Not logged in' };
    
    setIsLoading(true);
    try {
      const result = await apiUpdateProfile(user.user_id, updates);
      if (result.success) {
        setUser(prev => prev ? { ...prev, ...updates } : null);
        return { success: true };
      } else {
        return { success: false, error: result.error || 'Update failed' };
      }
    } catch (e) {
      return { success: false, error: 'Network error' };
    } finally {
      setIsLoading(false);
    }
  }, [user?.user_id]);

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      error,
      eligibleSchemes,
      missingFields,
      login,
      logout,
      updateProfile,
      refreshSchemes,
      refreshMissingFields,
      refreshProfile,
      answerMissingField
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
