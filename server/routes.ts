import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { 
  insertUserSchema, loginSchema, insertOrderSchema, insertCartItemSchema,
  type User, type Product
} from "@shared/schema";
import { z } from "zod";

// Simple session management
const sessions = new Map<string, { userId?: number; sessionId: string }>();

function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export async function registerRoutes(app: Express): Promise<Server> {
  // Middleware to handle sessions
  app.use('/api', (req, res, next) => {
    const sessionToken = req.headers.authorization?.replace('Bearer ', '') || req.headers['session-id'] as string;
    
    if (sessionToken && sessions.has(sessionToken)) {
      req.session = sessions.get(sessionToken);
    } else {
      const newSessionId = generateSessionId();
      const session = { sessionId: newSessionId };
      sessions.set(newSessionId, session);
      req.session = session;
      res.setHeader('session-id', newSessionId);
    }
    
    next();
  });

  // Authentication routes
  app.post('/api/auth/register', async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      
      // Check if user already exists
      const existingUser = await storage.getUserByEmail(userData.email);
      if (existingUser) {
        return res.status(400).json({ message: "Пользователь с таким email уже существует" });
      }
      
      const user = await storage.createUser(userData);
      const { password, ...userWithoutPassword } = user;
      
      // Create session
      const sessionToken = generateSessionId();
      sessions.set(sessionToken, { userId: user.id, sessionId: sessionToken });
      
      res.json({ user: userWithoutPassword, sessionToken });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Неверные данные", errors: error.errors });
      } else {
        res.status(500).json({ message: "Внутренняя ошибка сервера" });
      }
    }
  });

  app.post('/api/auth/login', async (req, res) => {
    try {
      const { email, password } = loginSchema.parse(req.body);
      
      const user = await storage.getUserByEmail(email);
      if (!user || user.password !== password) {
        return res.status(401).json({ message: "Неверный email или пароль" });
      }
      
      const { password: _, ...userWithoutPassword } = user;
      
      // Create session
      const sessionToken = generateSessionId();
      sessions.set(sessionToken, { userId: user.id, sessionId: sessionToken });
      
      res.json({ user: userWithoutPassword, sessionToken });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Неверные данные", errors: error.errors });
      } else {
        res.status(500).json({ message: "Внутренняя ошибка сервера" });
      }
    }
  });

  app.post('/api/auth/logout', async (req, res) => {
    const sessionToken = req.headers.authorization?.replace('Bearer ', '') || req.headers['session-id'] as string;
    if (sessionToken) {
      sessions.delete(sessionToken);
    }
    res.json({ message: "Успешный выход" });
  });

  app.get('/api/auth/me', async (req, res) => {
    if (!req.session?.userId) {
      return res.status(401).json({ message: "Не авторизован" });
    }
    
    const user = await storage.getUser(req.session.userId);
    if (!user) {
      return res.status(404).json({ message: "Пользователь не найден" });
    }
    
    const { password, ...userWithoutPassword } = user;
    res.json(userWithoutPassword);
  });

  // Products routes
  app.get('/api/products', async (req, res) => {
    try {
      const { brand, algorithm, priceMin, priceMax, inStock } = req.query;
      
      const filters = {
        brand: brand as string,
        algorithm: algorithm as string,
        priceMin: priceMin ? parseFloat(priceMin as string) : undefined,
        priceMax: priceMax ? parseFloat(priceMax as string) : undefined,
        inStock: inStock ? inStock === 'true' : undefined,
      };
      
      const products = Object.keys(filters).some(key => filters[key as keyof typeof filters] !== undefined)
        ? await storage.getProductsByFilter(filters)
        : await storage.getProducts();
      
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Ошибка получения продуктов" });
    }
  });

  app.get('/api/products/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const product = await storage.getProduct(id);
      
      if (!product) {
        return res.status(404).json({ message: "Продукт не найден" });
      }
      
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: "Ошибка получения продукта" });
    }
  });

  // Cart routes
  app.get('/api/cart', async (req, res) => {
    try {
      const userId = req.session?.userId;
      const sessionId = req.session?.sessionId;
      
      const cartItems = await storage.getCartItems(userId, sessionId);
      res.json(cartItems);
    } catch (error) {
      res.status(500).json({ message: "Ошибка получения корзины" });
    }
  });

  app.post('/api/cart', async (req, res) => {
    try {
      const cartData = insertCartItemSchema.parse(req.body);
      
      // Set user or session ID
      if (req.session?.userId) {
        cartData.userId = req.session.userId;
      } else {
        cartData.sessionId = req.session?.sessionId;
      }
      
      const cartItem = await storage.addToCart(cartData);
      res.json(cartItem);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Неверные данные", errors: error.errors });
      } else {
        res.status(500).json({ message: "Ошибка добавления в корзину" });
      }
    }
  });

  app.put('/api/cart/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { quantity } = req.body;
      
      if (!quantity || quantity < 1) {
        return res.status(400).json({ message: "Неверное количество" });
      }
      
      const updatedItem = await storage.updateCartItem(id, quantity);
      if (!updatedItem) {
        return res.status(404).json({ message: "Элемент корзины не найден" });
      }
      
      res.json(updatedItem);
    } catch (error) {
      res.status(500).json({ message: "Ошибка обновления корзины" });
    }
  });

  app.delete('/api/cart/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.removeFromCart(id);
      
      if (!success) {
        return res.status(404).json({ message: "Элемент корзины не найден" });
      }
      
      res.json({ message: "Элемент удален из корзины" });
    } catch (error) {
      res.status(500).json({ message: "Ошибка удаления из корзины" });
    }
  });

  app.delete('/api/cart', async (req, res) => {
    try {
      const userId = req.session?.userId;
      const sessionId = req.session?.sessionId;
      
      await storage.clearCart(userId, sessionId);
      res.json({ message: "Корзина очищена" });
    } catch (error) {
      res.status(500).json({ message: "Ошибка очистки корзины" });
    }
  });

  // Orders routes
  app.post('/api/orders', async (req, res) => {
    try {
      const orderData = insertOrderSchema.parse(req.body);
      
      // Set user ID if authenticated
      if (req.session?.userId) {
        orderData.userId = req.session.userId;
      }
      
      const order = await storage.createOrder(orderData);
      
      // Get cart items to create order items
      const cartItems = await storage.getCartItems(req.session?.userId, req.session?.sessionId);
      
      // Create order items
      for (const cartItem of cartItems) {
        await storage.createOrderItem({
          orderId: order.id,
          productId: cartItem.productId,
          quantity: cartItem.quantity,
          price: cartItem.product.price,
        });
      }
      
      // Clear cart after order creation
      await storage.clearCart(req.session?.userId, req.session?.sessionId);
      
      res.json(order);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Неверные данные заказа", errors: error.errors });
      } else {
        res.status(500).json({ message: "Ошибка создания заказа" });
      }
    }
  });

  app.get('/api/orders', async (req, res) => {
    try {
      if (!req.session?.userId) {
        return res.status(401).json({ message: "Необходима авторизация" });
      }
      
      const orders = await storage.getOrdersByUser(req.session.userId);
      res.json(orders);
    } catch (error) {
      res.status(500).json({ message: "Ошибка получения заказов" });
    }
  });

  app.get('/api/orders/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const order = await storage.getOrder(id);
      
      if (!order) {
        return res.status(404).json({ message: "Заказ не найден" });
      }
      
      // Check if user owns this order or is admin
      if (req.session?.userId && order.userId !== req.session.userId) {
        return res.status(403).json({ message: "Нет доступа к заказу" });
      }
      
      const orderItems = await storage.getOrderItems(id);
      res.json({ ...order, items: orderItems });
    } catch (error) {
      res.status(500).json({ message: "Ошибка получения заказа" });
    }
  });

  // User profile routes
  app.put('/api/profile', async (req, res) => {
    try {
      if (!req.session?.userId) {
        return res.status(401).json({ message: "Необходима авторизация" });
      }
      
      const updates = insertUserSchema.partial().parse(req.body);
      const updatedUser = await storage.updateUser(req.session.userId, updates);
      
      if (!updatedUser) {
        return res.status(404).json({ message: "Пользователь не найден" });
      }
      
      const { password, ...userWithoutPassword } = updatedUser;
      res.json(userWithoutPassword);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Неверные данные", errors: error.errors });
      } else {
        res.status(500).json({ message: "Ошибка обновления профиля" });
      }
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

// Extend Express Request interface to include session
declare global {
  namespace Express {
    interface Request {
      session?: { userId?: number; sessionId: string };
    }
  }
}
