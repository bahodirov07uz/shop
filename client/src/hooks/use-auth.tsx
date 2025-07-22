import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUser, login as authLogin, register as authRegister, logout as authLogout } from '@/lib/auth';
import type { User, LoginData, InsertUser } from '@shared/schema';

interface AuthContextType {
  user: User | null | undefined;
  isLoading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: InsertUser) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: authLogin,
    onSuccess: (data) => {
      queryClient.setQueryData(['auth', 'me'], data.user);
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: authRegister,
    onSuccess: (data) => {
      queryClient.setQueryData(['auth', 'me'], data.user);
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authLogout,
    onSuccess: () => {
      queryClient.setQueryData(['auth', 'me'], null);
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.clear();
    },
  });

  const login = async (data: LoginData) => {
    await loginMutation.mutateAsync(data);
  };

  const register = async (data: InsertUser) => {
    await registerMutation.mutateAsync(data);
  };

  const logout = async () => {
    await logoutMutation.mutateAsync();
  };

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated,
      }}
    >
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
