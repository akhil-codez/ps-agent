const API_BASE = 'https://ps-agent-api.onrender.com';

export interface UserProfile {
  user_id: string;
  name: string;
  phone: string;
  district: string;
  category: string;
  income: number;
  age: number;
  family_size: number;
  language: string;
  notify: number;
  // New granular fields
  gender?: 'male' | 'female' | 'other';
  employment_status?: 'employed' | 'unemployed' | 'self_employed' | 'govt_employee';
  marital_status?: 'married' | 'unmarried' | 'widowed' | 'divorced';
  education_level?: 'primary' | 'secondary' | 'higher_secondary' | 'graduate' | 'post_graduate';
  occupation?: string;
  house_ownership?: 'owned' | 'rented' | 'shelter' | 'none';
  vehicle_type?: 'none' | 'two_wheeler' | 'four_wheeler' | 'both';
  has_health_insurance?: boolean;
  has_life_insurance?: boolean;
  is_urban?: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface LoginResponse {
  success: boolean;
  user_id?: string;
  profile?: UserProfile;
  error?: string;
  message?: string;
}

export interface RegisterResponse {
  success: boolean;
  user_id?: string;
  message?: string;
  errors?: string[];
}

export interface ChatResponse {
  success: boolean;
  response?: string;
  error?: string;
}

export interface Notification {
  id: number;
  scheme_name: string;
  message_en?: string;
  message_ml?: string;
  is_read: boolean;
  created_at: string;
}

export interface Scheme {
  scheme_name: string;
  eligible: boolean | null;
  reason?: string;
  benefit?: string;
  documents_needed?: string[];
  application_portal?: string;
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 3
): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;
      if (i === retries - 1) return response;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    } catch (e) {
      if (i === retries - 1) throw e;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
  throw new Error('Max retries exceeded');
}

export async function login(phone: string, password: string): Promise<LoginResponse> {
  const response = await fetchWithRetry(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, password })
  });
  return response.json();
}

export async function register(data: {
  name: string;
  phone: string;
  password: string;
  district: string;
  category: string;
  income: number;
  age: number;
  family_size: number;
  language: string;
}): Promise<RegisterResponse> {
  const response = await fetchWithRetry(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}

export async function getProfile(userId: string): Promise<{ success: boolean; profile?: UserProfile; error?: string }> {
  const response = await fetchWithRetry(`${API_BASE}/profile/${userId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

export async function updateProfile(userId: string, updates: Partial<UserProfile>): Promise<{ success: boolean; error?: string }> {
  const response = await fetchWithRetry(`${API_BASE}/profile/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, updates })
  });
  return response.json();
}

export async function sendMessage(userId: string, message: string, isFirst: boolean = false): Promise<ChatResponse> {
  const response = await fetchWithRetry(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message, is_first: isFirst })
  });
  return response.json();
}

export async function getNotifications(userId: string): Promise<{ success: boolean; notifications: Notification[] }> {
  const response = await fetchWithRetry(`${API_BASE}/notifications/${userId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

export async function markNotificationRead(notificationId: number): Promise<{ success: boolean }> {
  const response = await fetchWithRetry(`${API_BASE}/notifications/${notificationId}/read`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

export async function getEligibleSchemes(userId: string): Promise<{
  success: boolean;
  eligible_schemes: Scheme[];
  not_eligible_schemes: Scheme[];
  unknown_schemes: Scheme[];
  total_schemes: number;
}> {
  const response = await fetchWithRetry(`${API_BASE}/schemes/eligible/${userId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

export interface MissingField {
  scheme: string;
  field: string;
  question_en: string;
  question_ml: string;
  input_type: string;
}

export async function getMissingEligibilityFields(userId: string): Promise<{
  success: boolean;
  missing_fields: MissingField[];
  total_missing: number;
}> {
  const response = await fetchWithRetry(`${API_BASE}/schemes/missing-fields/${userId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

export async function saveEligibilityAnswer(userId: string, field: string, value: string): Promise<{
  success: boolean;
}> {
  const response = await fetchWithRetry(`${API_BASE}/eligibility/save-answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, field, value })
  });
  return response.json();
}

export async function getServices(): Promise<{
  success: boolean;
  services: { key: string; name: string; description: string; subtypes: string[] }[];
}> {
  const response = await fetchWithRetry(`${API_BASE}/services`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}

// Conversation Management
export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

interface ConversationsStore {
  conversations: Conversation[];
  activeConversationId: string | null;
}

const MAX_CONVERSATIONS = 50;

function getConversationsStoreKey(userId: string): string {
  return `ps_conversations_${userId}`;
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function getConversationsStore(userId: string): ConversationsStore {
  try {
    const store = localStorage.getItem(getConversationsStoreKey(userId));
    return store ? JSON.parse(store) : { conversations: [], activeConversationId: null };
  } catch {
    return { conversations: [], activeConversationId: null };
  }
}

function saveConversationsStore(userId: string, store: ConversationsStore): void {
  try {
    // Keep only last MAX_CONVERSATIONS
    if (store.conversations.length > MAX_CONVERSATIONS) {
      store.conversations = store.conversations
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
        .slice(0, MAX_CONVERSATIONS);
    }
    localStorage.setItem(getConversationsStoreKey(userId), JSON.stringify(store));
  } catch (e) {
    console.error('Failed to save conversations:', e);
  }
}

export function getAllConversations(userId: string): Conversation[] {
  const store = getConversationsStore(userId);
  return store.conversations.sort((a, b) => 
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
}

export function getActiveConversation(userId: string): Conversation | null {
  const store = getConversationsStore(userId);
  if (!store.activeConversationId) return null;
  return store.conversations.find(c => c.id === store.activeConversationId) || null;
}

export function createConversation(userId: string, firstMessage: string = ''): Conversation {
  const store = getConversationsStore(userId);
  
  const newConversation: Conversation = {
    id: generateId(),
    title: firstMessage.substring(0, 40) || 'New conversation',
    messages: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  store.conversations.unshift(newConversation);
  store.activeConversationId = newConversation.id;
  saveConversationsStore(userId, store);
  
  return newConversation;
}

export function updateConversation(userId: string, convId: string, messages: ChatMessage[], firstMessage: string = ''): void {
  const store = getConversationsStore(userId);
  const conv = store.conversations.find(c => c.id === convId);
  
  if (conv) {
    conv.messages = messages;
    conv.updatedAt = new Date().toISOString();
    if (firstMessage && conv.messages.length === 1) {
      conv.title = firstMessage.substring(0, 40);
    }
    saveConversationsStore(userId, store);
  }
}

export function setActiveConversation(userId: string, convId: string | null): void {
  const store = getConversationsStore(userId);
  store.activeConversationId = convId;
  saveConversationsStore(userId, store);
}

export function deleteConversation(userId: string, convId: string): void {
  const store = getConversationsStore(userId);
  store.conversations = store.conversations.filter(c => c.id !== convId);
  
  if (store.activeConversationId === convId) {
    store.activeConversationId = store.conversations[0]?.id || null;
  }
  saveConversationsStore(userId, store);
}

// Legacy functions for backward compatibility
export function getChatHistory(userId: string): ChatMessage[] {
  const conv = getActiveConversation(userId);
  return conv?.messages || [];
}

export function saveChatHistory(userId: string, messages: ChatMessage[]): void {
  const store = getConversationsStore(userId);
  if (store.activeConversationId) {
    updateConversation(userId, store.activeConversationId, messages);
  }
}

export function clearChatHistory(userId: string): void {
  const store = getConversationsStore(userId);
  if (store.activeConversationId) {
    deleteConversation(userId, store.activeConversationId);
  }
}
