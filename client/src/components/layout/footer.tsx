import { Link } from 'wouter';
import { Microchip, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer-bg text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Microchip className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">ASIC-STORE</span>
            </div>
            <p className="text-gray-300 text-sm">
              Профессиональное криптовалютное оборудование для добычи Bitcoin, Litecoin и других криптовалют.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-300 hover:text-primary transition-colors">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </a>
              <a href="#" className="text-gray-300 hover:text-primary transition-colors">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                </svg>
              </a>
              <a href="#" className="text-gray-300 hover:text-primary transition-colors">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Catalog */}
          <div className="space-y-4">
            <h6 className="text-white font-semibold">Каталог</h6>
            <div className="space-y-2">
              <Link href="/catalog">
                <a className="block text-gray-300 hover:text-primary transition-colors text-sm">
                  ASIC майнеры
                </a>
              </Link>
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Запчасти
              </a>
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Аксессуары
              </a>
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Распродажа
              </a>
            </div>
          </div>

          {/* Information */}
          <div className="space-y-4">
            <h6 className="text-white font-semibold">Информация</h6>
            <div className="space-y-2">
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Оплата и доставка
              </a>
              <Link href="/about">
                <a className="block text-gray-300 hover:text-primary transition-colors text-sm">
                  О компании
                </a>
              </Link>
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Гарантия
              </a>
              <a href="#" className="block text-gray-300 hover:text-primary transition-colors text-sm">
                Контакты
              </a>
            </div>
          </div>

          {/* Contacts */}
          <div className="space-y-4">
            <h6 className="text-white font-semibold">Контакты</h6>
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-gray-300 text-sm">
                <Mail className="h-4 w-4" />
                <span>info@asic-store.com</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-300 text-sm">
                <Phone className="h-4 w-4" />
                <span>+1-909-390-7780</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-300 text-sm">
                <MapPin className="h-4 w-4" />
                <span>China, Shenzhen</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Bottom */}
        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-gray-400 text-sm">
            &copy; 2024 ASIC-STORE. Все права защищены.
          </p>
        </div>
      </div>
    </footer>
  );
}
