import { createContext, useContext, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { addAuthHeaders } from '@/lib/auth';
import type { CartItem, Product, InsertCartItem } from '@shared/schema';

interface CartContextType {
  cartItems: (CartItem & { product: Product })[];
  isLoading: boolean;
  addToCart: (productId: number, quantity?: number) => Promise<void>;
  updateCartItem: (id: number, quantity: number) => Promise<void>;
  removeFromCart: (id: number) => Promise<void>;
  clearCart: () => Promise<void>;
  cartTotal: number;
  cartCount: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const { data: cartItems = [], isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: async () => {
      const response = await fetch('/api/cart', {
        headers: addAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch cart');
      return response.json();
    },
  });

  const addToCartMutation = useMutation({
    mutationFn: async ({ productId, quantity = 1 }: { productId: number; quantity?: number }) => {
      const response = await apiRequest('POST', '/api/cart', { productId, quantity });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const updateCartMutation = useMutation({
    mutationFn: async ({ id, quantity }: { id: number; quantity: number }) => {
      const response = await apiRequest('PUT', `/api/cart/${id}`, { quantity });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const removeFromCartMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await apiRequest('DELETE', `/api/cart/${id}`);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const clearCartMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest('DELETE', '/api/cart');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const addToCart = async (productId: number, quantity = 1) => {
    await addToCartMutation.mutateAsync({ productId, quantity });
  };

  const updateCartItem = async (id: number, quantity: number) => {
    await updateCartMutation.mutateAsync({ id, quantity });
  };

  const removeFromCart = async (id: number) => {
    await removeFromCartMutation.mutateAsync(id);
  };

  const clearCart = async () => {
    await clearCartMutation.mutateAsync();
  };

  const cartTotal = cartItems.reduce((total: number, item: any) => {
    return total + parseFloat(item.product.price) * item.quantity;
  }, 0);

  const cartCount = cartItems.reduce((count: number, item: any) => count + item.quantity, 0);

  return (
    <CartContext.Provider
      value={{
        cartItems,
        isLoading,
        addToCart,
        updateCartItem,
        removeFromCart,
        clearCart,
        cartTotal,
        cartCount,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
