import { 
  users, products, orders, orderItems, cartItems,
  type User, type InsertUser, type Product, type InsertProduct,
  type Order, type InsertOrder, type OrderItem, type InsertOrderItem,
  type CartItem, type InsertCartItem
} from "@shared/schema";

export interface IStorage {
  // User operations
  getUser(id: number): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: number, updates: Partial<InsertUser>): Promise<User | undefined>;
  
  // Product operations
  getProducts(): Promise<Product[]>;
  getProduct(id: number): Promise<Product | undefined>;
  getProductsByFilter(filters: {
    brand?: string;
    algorithm?: string;
    priceMin?: number;
    priceMax?: number;
    inStock?: boolean;
  }): Promise<Product[]>;
  createProduct(product: InsertProduct): Promise<Product>;
  
  // Order operations
  createOrder(order: InsertOrder): Promise<Order>;
  getOrdersByUser(userId: number): Promise<Order[]>;
  getOrder(id: number): Promise<Order | undefined>;
  updateOrderStatus(id: number, status: string): Promise<Order | undefined>;
  
  // Order items operations
  createOrderItem(item: InsertOrderItem): Promise<OrderItem>;
  getOrderItems(orderId: number): Promise<OrderItem[]>;
  
  // Cart operations
  getCartItems(userId?: number, sessionId?: string): Promise<(CartItem & { product: Product })[]>;
  addToCart(item: InsertCartItem): Promise<CartItem>;
  updateCartItem(id: number, quantity: number): Promise<CartItem | undefined>;
  removeFromCart(id: number): Promise<boolean>;
  clearCart(userId?: number, sessionId?: string): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private products: Map<number, Product>;
  private orders: Map<number, Order>;
  private orderItems: Map<number, OrderItem>;
  private cartItems: Map<number, CartItem>;
  private currentUserId: number = 1;
  private currentProductId: number = 1;
  private currentOrderId: number = 1;
  private currentOrderItemId: number = 1;
  private currentCartItemId: number = 1;

  constructor() {
    this.users = new Map();
    this.products = new Map();
    this.orders = new Map();
    this.orderItems = new Map();
    this.cartItems = new Map();
    
    this.initializeData();
  }

  private initializeData() {
    // Sample products data
    const sampleProducts: InsertProduct[] = [
      {
        name: "Bitmain Antminer L9 17 GH/s",
        brand: "Bitmain",
        model: "Antminer L9",
        algorithm: "Scrypt",
        hashrate: "17 GH/s",
        powerConsumption: 3360,
        price: "2549.00",
        oldPrice: "3186.00",
        imageUrl: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Профессиональный ASIC-майнер для добычи Litecoin и других криптовалют на алгоритме Scrypt",
        badge: "sale",
        specifications: JSON.stringify({
          algorithm: "Scrypt",
          hashrate: "17 GH/s ±5%",
          powerConsumption: "3360W ±5%",
          powerEfficiency: "0.19 J/MH ±5%",
          operatingTemperature: "0°C to 40°C",
          networkConnection: "Ethernet",
          dimensions: "430×195.5×290.5 mm"
        })
      },
      {
        name: "Bitmain Antminer S19 Pro 110 TH/s",
        brand: "Bitmain",
        model: "Antminer S19 Pro",
        algorithm: "SHA-256",
        hashrate: "110 TH/s",
        powerConsumption: 3250,
        price: "3299.00",
        imageUrl: "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Высокопроизводительный ASIC-майнер для добычи Bitcoin",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "110 TH/s ±5%",
          powerConsumption: "3250W ±5%",
          powerEfficiency: "29.5 J/TH ±5%"
        })
      },
      {
        name: "WhatsMiner M50 118 TH/s",
        brand: "MicroBT",
        model: "WhatsMiner M50",
        algorithm: "SHA-256",
        hashrate: "118 TH/s",
        powerConsumption: 3276,
        price: "3499.00",
        imageUrl: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Мощный ASIC-майнер от MicroBT для добычи Bitcoin",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "118 TH/s ±5%",
          powerConsumption: "3276W ±5%",
          powerEfficiency: "27.8 J/TH ±5%"
        })
      },
      {
        name: "Avalon A1246 90 TH/s",
        brand: "Canaan",
        model: "Avalon A1246",
        algorithm: "SHA-256",
        hashrate: "90 TH/s",
        powerConsumption: 3420,
        price: "2899.00",
        imageUrl: "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Надежный ASIC-майнер от Canaan",
        badge: "new",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "90 TH/s ±5%",
          powerConsumption: "3420W ±5%",
          powerEfficiency: "38 J/TH ±5%"
        })
      },
      {
        name: "Bitmain Antminer S19j Pro 104 TH/s",
        brand: "Bitmain",
        model: "Antminer S19j Pro",
        algorithm: "SHA-256",
        hashrate: "104 TH/s",
        powerConsumption: 3068,
        price: "3199.00",
        imageUrl: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Энергоэффективный ASIC-майнер для Bitcoin",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "104 TH/s ±5%",
          powerConsumption: "3068W ±5%",
          powerEfficiency: "29.5 J/TH ±5%"
        })
      },
      {
        name: "WhatsMiner M31S+ 80 TH/s",
        brand: "MicroBT",
        model: "WhatsMiner M31S+",
        algorithm: "SHA-256",
        hashrate: "80 TH/s",
        powerConsumption: 3472,
        price: "2699.00",
        imageUrl: "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Стабильный ASIC-майнер для длительной работы",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "80 TH/s ±5%",
          powerConsumption: "3472W ±5%",
          powerEfficiency: "43.4 J/TH ±5%"
        })
      },
      {
        name: "Bitmain Antminer T19 84 TH/s",
        brand: "Bitmain",
        model: "Antminer T19",
        algorithm: "SHA-256",
        hashrate: "84 TH/s",
        powerConsumption: 3150,
        price: "2399.00",
        oldPrice: "2822.00",
        imageUrl: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Доступный ASIC-майнер с хорошим соотношением цена/производительность",
        badge: "sale",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "84 TH/s ±5%",
          powerConsumption: "3150W ±5%",
          powerEfficiency: "37.5 J/TH ±5%"
        })
      },
      {
        name: "Avalon A1166 Pro 75 TH/s",
        brand: "Canaan",
        model: "Avalon A1166 Pro",
        algorithm: "SHA-256",
        hashrate: "75 TH/s",
        powerConsumption: 3250,
        price: "2599.00",
        imageUrl: "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300",
        description: "Профессиональный ASIC-майнер от Canaan",
        specifications: JSON.stringify({
          algorithm: "SHA-256",
          hashrate: "75 TH/s ±5%",
          powerConsumption: "3250W ±5%",
          powerEfficiency: "43.3 J/TH ±5%"
        })
      }
    ];

    // Add sample products
    sampleProducts.forEach(product => {
      const id = this.currentProductId++;
      this.products.set(id, { 
        ...product, 
        id,
        description: product.description || null,
        inStock: product.inStock ?? true,
        createdAt: new Date()
      });
    });
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.email === email);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { 
      ...insertUser,
      id,
      address: insertUser.address || null,
      phone: insertUser.phone || null,
      country: insertUser.country || null,
      city: insertUser.city || null,
      isActive: true,
      createdAt: new Date()
    };
    this.users.set(id, user);
    return user;
  }

  async updateUser(id: number, updates: Partial<InsertUser>): Promise<User | undefined> {
    const user = this.users.get(id);
    if (!user) return undefined;
    
    const updatedUser = { ...user, ...updates };
    this.users.set(id, updatedUser);
    return updatedUser;
  }

  async getProducts(): Promise<Product[]> {
    return Array.from(this.products.values());
  }

  async getProduct(id: number): Promise<Product | undefined> {
    return this.products.get(id);
  }

  async getProductsByFilter(filters: {
    brand?: string;
    algorithm?: string;
    priceMin?: number;
    priceMax?: number;
    inStock?: boolean;
  }): Promise<Product[]> {
    return Array.from(this.products.values()).filter(product => {
      if (filters.brand && product.brand !== filters.brand) return false;
      if (filters.algorithm && product.algorithm !== filters.algorithm) return false;
      if (filters.priceMin && parseFloat(product.price) < filters.priceMin) return false;
      if (filters.priceMax && parseFloat(product.price) > filters.priceMax) return false;
      if (filters.inStock !== undefined && product.inStock !== filters.inStock) return false;
      return true;
    });
  }

  async createProduct(insertProduct: InsertProduct): Promise<Product> {
    const id = this.currentProductId++;
    const product: Product = { 
      ...insertProduct, 
      id,
      description: insertProduct.description || null,
      inStock: true,
      createdAt: new Date()
    };
    this.products.set(id, product);
    return product;
  }

  async createOrder(insertOrder: InsertOrder): Promise<Order> {
    const id = this.currentOrderId++;
    const order: Order = { 
      ...insertOrder, 
      id,
      userId: insertOrder.userId || null,
      comment: insertOrder.comment || null,
      status: "pending",
      createdAt: new Date()
    };
    this.orders.set(id, order);
    return order;
  }

  async getOrdersByUser(userId: number): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(order => order.userId === userId);
  }

  async getOrder(id: number): Promise<Order | undefined> {
    return this.orders.get(id);
  }

  async updateOrderStatus(id: number, status: string): Promise<Order | undefined> {
    const order = this.orders.get(id);
    if (!order) return undefined;
    
    const updatedOrder = { ...order, status };
    this.orders.set(id, updatedOrder);
    return updatedOrder;
  }

  async createOrderItem(insertItem: InsertOrderItem): Promise<OrderItem> {
    const id = this.currentOrderItemId++;
    const item: OrderItem = { ...insertItem, id };
    this.orderItems.set(id, item);
    return item;
  }

  async getOrderItems(orderId: number): Promise<OrderItem[]> {
    return Array.from(this.orderItems.values()).filter(item => item.orderId === orderId);
  }

  async getCartItems(userId?: number, sessionId?: string): Promise<(CartItem & { product: Product })[]> {
    const items = Array.from(this.cartItems.values()).filter(item => {
      if (userId) return item.userId === userId;
      if (sessionId) return item.sessionId === sessionId;
      return false;
    });

    return items.map(item => {
      const product = this.products.get(item.productId);
      return { ...item, product: product! };
    }).filter(item => item.product);
  }

  async addToCart(insertItem: InsertCartItem): Promise<CartItem> {
    // Check if item already exists in cart
    const existingItem = Array.from(this.cartItems.values()).find(item => {
      if (insertItem.userId && item.userId === insertItem.userId && item.productId === insertItem.productId) return true;
      if (insertItem.sessionId && item.sessionId === insertItem.sessionId && item.productId === insertItem.productId) return true;
      return false;
    });

    if (existingItem) {
      // Update quantity
      const updatedItem = { ...existingItem, quantity: existingItem.quantity + insertItem.quantity };
      this.cartItems.set(existingItem.id, updatedItem);
      return updatedItem;
    } else {
      // Create new item
      const id = this.currentCartItemId++;
      const item: CartItem = { 
        ...insertItem, 
        id,
        userId: insertItem.userId || null,
        sessionId: insertItem.sessionId || null,
        createdAt: new Date()
      };
      this.cartItems.set(id, item);
      return item;
    }
  }

  async updateCartItem(id: number, quantity: number): Promise<CartItem | undefined> {
    const item = this.cartItems.get(id);
    if (!item) return undefined;
    
    const updatedItem = { ...item, quantity };
    this.cartItems.set(id, updatedItem);
    return updatedItem;
  }

  async removeFromCart(id: number): Promise<boolean> {
    return this.cartItems.delete(id);
  }

  async clearCart(userId?: number, sessionId?: string): Promise<boolean> {
    const items = Array.from(this.cartItems.entries()).filter(([_, item]) => {
      if (userId) return item.userId === userId;
      if (sessionId) return item.sessionId === sessionId;
      return false;
    });

    items.forEach(([id]) => this.cartItems.delete(id));
    return true;
  }
}

export const storage = new MemStorage();
