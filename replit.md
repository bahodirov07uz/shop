# ASIC Store - Cryptocurrency Mining Equipment E-commerce Platform

## Overview

This is a full-stack e-commerce application built for selling ASIC cryptocurrency mining equipment. The application features a React frontend with TypeScript, Express.js backend, and PostgreSQL database using Drizzle ORM. It includes user authentication, product catalog, shopping cart, and order management functionality.

## User Preferences

Preferred communication style: Simple, everyday language.
Development preference: Frontend-only solutions, user will handle backend implementation separately.
Design style: Professional, clean design based on provided samples with ASIC miner focus.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter for client-side routing
- **State Management**: TanStack React Query for server state, React Context for local state
- **UI Components**: Radix UI primitives with shadcn/ui component library
- **Styling**: Tailwind CSS with CSS variables for theming
- **Form Handling**: React Hook Form with Zod validation

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Database**: PostgreSQL with Drizzle ORM
- **Session Management**: Simple in-memory session storage with bearer tokens
- **API Design**: RESTful API with JSON responses
- **File Structure**: Monorepo structure with shared schema between client and server

### Data Storage
- **Database**: PostgreSQL (configured for Neon Database)
- **ORM**: Drizzle ORM with TypeScript schema definitions
- **Tables**: Users, Products, Orders, Order Items, Cart Items
- **Migrations**: Drizzle Kit for database migrations

## Key Components

### Authentication System
- Session-based authentication with bearer tokens
- In-memory session storage (suitable for development, should be replaced with Redis/database for production)
- User registration and login with password validation
- Protected routes and API endpoints

### Product Management
- Product catalog with filtering capabilities (brand, algorithm, price range, stock status)
- Product details with specifications stored as JSON
- Search functionality across product names and descriptions
- Product images and badges (new, sale, etc.)

### Shopping Cart
- Session-based cart for anonymous users
- User-based cart for authenticated users
- Real-time cart updates with optimistic UI
- Cart persistence across sessions

### Order Processing
- Complete order checkout flow
- Customer information collection
- Multiple payment method support (credit card, crypto, bank transfer)
- Order status tracking

### UI/UX Features
- Responsive design with mobile-first approach
- Dark/light theme support
- Toast notifications for user feedback
- Loading states and error handling
- Accessible components using Radix UI

## Data Flow

1. **User Authentication**: Users can register/login, sessions are managed server-side
2. **Product Browsing**: Products are fetched from database with filtering and search
3. **Cart Management**: Items added to cart are stored per session/user
4. **Order Placement**: Cart items are converted to orders with customer details
5. **State Synchronization**: React Query manages server state with automatic cache invalidation

## External Dependencies

### Frontend Dependencies
- **UI Framework**: React, React DOM
- **Routing**: wouter
- **State Management**: @tanstack/react-query
- **Forms**: react-hook-form, @hookform/resolvers
- **Validation**: zod, drizzle-zod
- **UI Components**: @radix-ui/* components
- **Styling**: tailwindcss, class-variance-authority, clsx
- **Utilities**: date-fns, embla-carousel-react

### Backend Dependencies
- **Server**: express
- **Database**: @neondatabase/serverless, drizzle-orm
- **Development**: tsx, esbuild, vite
- **Session Storage**: connect-pg-simple (though currently using in-memory storage)

### Development Tools
- **Build System**: Vite for frontend, esbuild for backend
- **Database Tools**: drizzle-kit for migrations
- **TypeScript**: Full TypeScript support across the stack
- **Development Environment**: Replit-specific plugins and configurations

## Deployment Strategy

### Development
- Frontend served by Vite dev server with HMR
- Backend runs with tsx for TypeScript execution
- Database migrations handled by Drizzle Kit

### Production Build
- Frontend built with Vite to static assets
- Backend bundled with esbuild to single file
- Static assets served by Express in production
- Database connection via environment variable (DATABASE_URL)

### Environment Configuration
- PostgreSQL database (configured for Neon)
- Environment variables for database connection
- Session management (currently in-memory, should be upgraded for production)
- Replit-specific configurations for development environment

The application follows a standard full-stack architecture with clear separation between frontend and backend, shared type definitions, and modern development practices including TypeScript throughout, comprehensive error handling, and responsive design patterns.