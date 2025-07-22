import { apiRequest } from "./queryClient";
import type { User, LoginData, InsertUser } from "@shared/schema";

let sessionToken: string | null = localStorage.getItem('sessionToken');

export function setSessionToken(token: string) {
  sessionToken = token;
  localStorage.setItem('sessionToken', token);
}

export function getSessionToken() {
  return sessionToken;
}

export function clearSessionToken() {
  sessionToken = null;
  localStorage.removeItem('sessionToken');
}

export async function login(data: LoginData): Promise<{ user: User; sessionToken: string }> {
  const response = await apiRequest('POST', '/api/auth/login', data);
  const result = await response.json();
  setSessionToken(result.sessionToken);
  return result;
}

export async function register(data: InsertUser): Promise<{ user: User; sessionToken: string }> {
  const response = await apiRequest('POST', '/api/auth/register', data);
  const result = await response.json();
  setSessionToken(result.sessionToken);
  return result;
}

export async function logout(): Promise<void> {
  if (sessionToken) {
    await apiRequest('POST', '/api/auth/logout', undefined);
    clearSessionToken();
  }
}

export async function getCurrentUser(): Promise<User | null> {
  if (!sessionToken) return null;
  
  try {
    const response = await fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${sessionToken}`,
      },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        clearSessionToken();
        return null;
      }
      throw new Error('Failed to fetch user');
    }
    
    return await response.json();
  } catch (error) {
    clearSessionToken();
    return null;
  }
}

// Add authorization header to all requests
export function addAuthHeaders(headers: Record<string, string> = {}): Record<string, string> {
  if (sessionToken) {
    headers['Authorization'] = `Bearer ${sessionToken}`;
  }
  return headers;
}
