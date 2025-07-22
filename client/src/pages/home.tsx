import { Link } from 'wouter';
import { ArrowRight, Shield, Truck, Wrench, Bitcoin } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Home() {
  const trustIndicators = [
    {
      icon: Shield,
      title: "Гарантия качества",
      description: "Все оборудование проходит проверку и имеет официальную гарантию"
    },
    {
      icon: Truck,
      title: "Быстрая доставка",
      description: "Доставка в любую точку мира. Отслеживание посылки в реальном времени"
    },
    {
      icon: Wrench,
      title: "Техническая поддержка",
      description: "Профессиональная помощь в настройке и обслуживании оборудования"
    },
    {
      icon: Bitcoin,
      title: "Криптоплатежи",
      description: "Принимаем оплату в Bitcoin, Ethereum и других криптовалютах"
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="hero-gradient text-white py-16 lg:py-24">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="hero-title text-4xl lg:text-5xl font-bold leading-tight">
                Профессиональное криптооборудование
              </h1>
              <p className="hero-subtitle text-lg lg:text-xl opacity-90">
                Ведущий поставщик ASIC-майнеров для добычи криптовалют. Гарантия качества и надежная доставка.
              </p>
              <Link href="/catalog">
                <Button size="lg" variant="secondary" className="bg-white text-primary hover:bg-gray-100">
                  Смотреть каталог
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600"
                alt="ASIC mining farm"
                className="w-full rounded-3xl shadow-2xl"
                loading="eager"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-16 lg:py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {trustIndicators.map((item, index) => (
              <div key={index} className="trust-indicator text-center">
                <div className="trust-indicator-icon flex justify-center mb-6">
                  <item.icon className="h-12 w-12" />
                </div>
                <h3 className="font-semibold text-lg mb-3">{item.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Preview */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Популярные модели</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Лучшее оборудование для майнинга от ведущих производителей
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Featured product cards would go here */}
            <div className="bg-white rounded-xl p-6 shadow-sm text-center">
              <img
                src="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&h=200"
                alt="ASIC Miner"
                className="w-full h-40 object-cover rounded-lg mb-4"
              />
              <h3 className="font-semibold mb-2">Bitmain Antminer S19 Pro</h3>
              <p className="text-sm text-muted-foreground mb-3">110 TH/s, SHA-256</p>
              <p className="text-primary font-bold text-lg">$3,299</p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm text-center">
              <img
                src="https://images.unsplash.com/photo-1640340434855-6084b1f4901c?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&h=200"
                alt="ASIC Miner"
                className="w-full h-40 object-cover rounded-lg mb-4"
              />
              <h3 className="font-semibold mb-2">WhatsMiner M50</h3>
              <p className="text-sm text-muted-foreground mb-3">118 TH/s, SHA-256</p>
              <p className="text-primary font-bold text-lg">$3,499</p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm text-center">
              <img
                src="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&h=200"
                alt="ASIC Miner"
                className="w-full h-40 object-cover rounded-lg mb-4"
              />
              <h3 className="font-semibold mb-2">Bitmain Antminer L9</h3>
              <p className="text-sm text-muted-foreground mb-3">17 GH/s, Scrypt</p>
              <p className="text-primary font-bold text-lg">$2,549</p>
            </div>
          </div>
          
          <div className="text-center">
            <Link href="/catalog">
              <Button size="lg" className="btn-primary-green">
                Смотреть все товары
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
