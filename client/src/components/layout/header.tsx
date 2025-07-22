import { useState } from 'react';
import { Link, useLocation } from 'wouter';
import { Search, User, Heart, ShoppingCart, Menu, X, Microchip } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import LoginModal from '@/components/auth/login-modal';
import RegisterModal from '@/components/auth/register-modal';
import CartModal from '@/components/cart/cart-modal';
import { useAuth } from '@/hooks/use-auth';
import { useCart } from '@/hooks/use-cart';

export default function Header() {
  const [location] = useLocation();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showCartModal, setShowCartModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, isAuthenticated, logout } = useAuth();
  const { cartCount } = useCart();

  const navItems = [
    { href: '/catalog', label: 'ASIC майнеры' },
    { href: '/about', label: 'О компании' },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Navigate to catalog with search query
      window.location.href = `/catalog?search=${encodeURIComponent(searchQuery.trim())}`;
    }
  };

  const handleAuthAction = () => {
    if (isAuthenticated) {
      logout();
    } else {
      setShowLoginModal(true);
    }
  };

  return (
    <>
      <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2">
              <Microchip className="h-8 w-8 text-primary" />
              <span className="navbar-brand-text text-xl">ASIC-STORE</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href}>
                  <span className={`nav-link-custom ${location === item.href ? 'text-primary' : ''}`}>
                    {item.label}
                  </span>
                </Link>
              ))}
            </div>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-md mx-8">
              <form onSubmit={handleSearch} className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Поиск оборудования..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input w-full"
                />
              </form>
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleAuthAction}
                className="user-action-link hidden sm:flex"
              >
                <User className="h-5 w-5 mb-1" />
                <span className="text-xs">
                  {isAuthenticated ? user?.name || 'Профиль' : 'Войти'}
                </span>
              </Button>

              <Button variant="ghost" size="sm" className="user-action-link hidden sm:flex">
                <Heart className="h-5 w-5 mb-1" />
                <span className="text-xs">Избранное</span>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCartModal(true)}
                className="user-action-link relative"
              >
                <ShoppingCart className="h-5 w-5 mb-1" />
                {cartCount > 0 && (
                  <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                    {cartCount}
                  </Badge>
                )}
                <span className="text-xs hidden sm:block">Корзина</span>
              </Button>

              {/* Mobile Menu */}
              <Sheet>
                <SheetTrigger asChild className="lg:hidden">
                  <Button variant="ghost" size="sm">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent>
                  <div className="flex flex-col space-y-4 mt-8">
                    {/* Mobile Search */}
                    <form onSubmit={handleSearch} className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="text"
                        placeholder="Поиск..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </form>

                    {/* Mobile Navigation */}
                    {navItems.map((item) => (
                      <Link key={item.href} href={item.href}>
                        <Button variant="ghost" className="w-full justify-start">
                          {item.label}
                        </Button>
                      </Link>
                    ))}

                    <hr />

                    {/* Mobile User Actions */}
                    <Button variant="ghost" onClick={handleAuthAction} className="justify-start">
                      <User className="h-4 w-4 mr-2" />
                      {isAuthenticated ? user?.name || 'Профиль' : 'Войти'}
                    </Button>

                    <Button variant="ghost" className="justify-start">
                      <Heart className="h-4 w-4 mr-2" />
                      Избранное
                    </Button>

                    {isAuthenticated && (
                      <Link href="/account">
                        <Button variant="ghost" className="w-full justify-start">
                          Личный кабинет
                        </Button>
                      </Link>
                    )}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </nav>

      {/* Modals */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onSwitchToRegister={() => {
          setShowLoginModal(false);
          setShowRegisterModal(true);
        }}
      />

      <RegisterModal
        isOpen={showRegisterModal}
        onClose={() => setShowRegisterModal(false)}
        onSwitchToLogin={() => {
          setShowRegisterModal(false);
          setShowLoginModal(true);
        }}
      />

      <CartModal
        isOpen={showCartModal}
        onClose={() => setShowCartModal(false)}
      />
    </>
  );
}
