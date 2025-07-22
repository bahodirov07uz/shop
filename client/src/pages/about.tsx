import { CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function About() {
  const features = [
    "Более 5000 довольных клиентов",
    "Доставка в 50+ стран мира",
    "Официальная гарантия от производителя",
    "Техническая поддержка 24/7"
  ];

  const whyChooseUs = [
    {
      title: "Профессиональный подход",
      description: "Наша команда состоит из экспертов в области криптовалют и майнинга, которые помогут выбрать оптимальное оборудование для ваших задач."
    },
    {
      title: "Гарантия качества",
      description: "Мы работаем только с официальными поставщиками и предоставляем гарантию на все оборудование от производителей."
    },
    {
      title: "Индивидуальные решения",
      description: "Подберем оптимальную конфигурацию оборудования исходя из ваших потребностей, бюджета и условий эксплуатации."
    }
  ];

  const newsItems = [
    {
      title: "РБК",
      description: "Рынок криптовалютного оборудования показывает устойчивый рост",
      date: "15 дек 2024"
    },
    {
      title: "РОССИЯ 24",
      description: "Специальный репортаж о майнинговой индустрии",
      date: "8 ноя 2024"
    },
    {
      title: "RG.RU",
      description: "Интервью с экспертами рынка ASIC-оборудования",
      date: "22 окт 2024"
    },
    {
      title: "Коммерсантъ",
      description: "О перспективах развития криптовалютной индустрии",
      date: "1 окт 2024"
    }
  ];

  const offices = [
    {
      city: "Иркутский офис",
      address: "ул. Лермонтова 257, офис 719",
      phone: "+7 (3952) 48-38-20",
      image: "https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300"
    },
    {
      city: "Иркутский офис",
      address: "ул. Академика Образцова 28",
      phone: "+7 (3952) 48-38-20",
      image: "https://images.unsplash.com/photo-1497366754035-f200968a6e72?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300"
    },
    {
      city: "Офис в Санкт-Петербурге",
      address: "Обводного канала наб., 138к3",
      phone: "+7 (812) 309-52-99",
      image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300"
    }
  ];

  return (
    <div className="bg-gray-50">
      {/* Hero Section */}
      <section className="hero-gradient text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl lg:text-5xl font-bold mb-6">О компании</h1>
            <p className="text-xl opacity-90 mb-8">
              Мы являемся ведущим поставщиком профессионального криптовалютного оборудования для майнинга
            </p>
          </div>
        </div>
      </section>

      {/* Company Story */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl font-bold mb-6">История компании</h2>
              <p className="text-muted-foreground leading-relaxed">
                Компания основана в 2013 году и за это время зарекомендовала себя как надежный партнер для тысяч клиентов по всему миру. Мы предлагаем только оригинальное оборудование от ведущих производителей.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Доставка осуществляется Bitmain — ведущий производитель майнингового оборудования, известен своими высококачественными и эффективными майнерами Antminer.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Компания Bitmain — безусловный лидер по выпуску оборудования для майнинга криптовалют. С 2013-го ежегодно на рынок выходят обновленные ASICи, задающие планку всей индустрии. Это экономично, ведь именно здесь изобрели ASIC, что является одной из главных причин доверия к продукции производителя.
              </p>
              
              <ul className="space-y-3">
                {features.map((feature, index) => (
                  <li key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-primary flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600"
                alt="Data center"
                className="w-full rounded-3xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Почему нам доверяют</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Мы стремимся предоставить лучший сервис и качественное оборудование для наших клиентов
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {whyChooseUs.map((item, index) => (
              <Card key={index} className="h-full">
                <CardContent className="p-6 text-center">
                  <h3 className="font-semibold text-lg mb-3">{item.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {item.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* In the Media */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">О нас пишут</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {newsItems.map((item, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <Badge variant="outline" className="mb-3">
                    {item.title}
                  </Badge>
                  <h3 className="font-medium text-sm mb-2 line-clamp-3">
                    {item.description}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {item.date}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Offices */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Контакты</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {offices.map((office, index) => (
              <Card key={index} className="overflow-hidden">
                <div className="h-48">
                  <img
                    src={office.image}
                    alt={office.city}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardContent className="p-6">
                  <h3 className="font-semibold text-lg mb-2">{office.city}</h3>
                  <p className="text-muted-foreground text-sm mb-2">
                    {office.address}
                  </p>
                  <p className="text-primary font-medium text-sm">
                    {office.phone}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* World Map */}
          <div className="mt-12 bg-white rounded-xl p-8 shadow-sm">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold mb-2">Наша география</h3>
              <p className="text-muted-foreground">
                Мы работаем с клиентами по всему миру
              </p>
            </div>
            
            {/* Simplified world map representation */}
            <div className="relative bg-blue-50 rounded-lg h-64 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-4">🌍</div>
                <p className="text-muted-foreground">
                  Доставка в более чем 50 стран мира
                </p>
                <div className="flex justify-center space-x-6 mt-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-primary rounded-full"></div>
                    <span>Главные офисы</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                    <span>Партнеры</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                    <span>Склады</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
