import { useState } from 'react';
import { useParams, Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { ShoppingCart, Heart, Shield, Truck, Wrench, Check, ArrowLeft } from 'lucide-react';
import { useCart } from '@/hooks/use-cart';
import { useToast } from '@/hooks/use-toast';
import { addAuthHeaders } from '@/lib/auth';
import type { Product } from '@shared/schema';

export default function ProductDetail() {
  const params = useParams();
  const productId = params.id ? parseInt(params.id) : 0;
  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const { addToCart } = useCart();
  const { toast } = useToast();

  const { data: product, isLoading, error } = useQuery({
    queryKey: ['products', productId],
    queryFn: async () => {
      const response = await fetch(`/api/products/${productId}`, {
        headers: addAuthHeaders(),
      });
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Product not found');
        }
        throw new Error('Failed to fetch product');
      }
      return response.json();
    },
    enabled: productId > 0,
  });

  const handleAddToCart = async () => {
    if (!product || isAdding || justAdded) return;
    
    setIsAdding(true);
    
    try {
      await addToCart(product.id, 1);
      setJustAdded(true);
      toast({
        title: "Товар добавлен в корзину",
        description: `${product.name} успешно добавлен в корзину`,
      });
      
      setTimeout(() => setJustAdded(false), 3000);
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось добавить товар в корзину",
        variant: "destructive",
      });
    } finally {
      setIsAdding(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="h-96 bg-gray-200 rounded-lg"></div>
            <div className="space-y-4">
              <div className="h-8 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              <div className="h-6 bg-gray-200 rounded w-1/4"></div>
              <div className="h-12 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Товар не найден</h1>
          <p className="text-muted-foreground mb-6">
            Запрашиваемый товар не существует или был удален
          </p>
          <Link href="/catalog">
            <Button>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Вернуться к каталогу
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const specifications = product.specifications ? JSON.parse(product.specifications) : {};

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Breadcrumbs */}
      <div className="bg-white border-b py-4">
        <div className="container mx-auto px-4">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Главная</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink href="/catalog">Каталог</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>{product.name}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Product Image */}
          <div className="relative">
            <div className="bg-white rounded-xl p-8 shadow-sm">
              {product.badge && (
                <Badge className={`product-badge ${product.badge} absolute top-4 right-4 z-10`}>
                  {product.badge === 'sale' && '-20%'}
                  {product.badge === 'new' && 'Новинка'}
                </Badge>
              )}
              <img
                src={product.imageUrl}
                alt={product.name}
                className="w-full h-96 object-contain"
              />
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
              <p className="text-muted-foreground">
                {product.brand} • {product.model}
              </p>
            </div>

            {/* Basic Specs */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="font-semibold text-lg">{product.hashrate}</div>
                  <div className="text-sm text-muted-foreground">Хешрейт</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="font-semibold text-lg">{product.algorithm}</div>
                  <div className="text-sm text-muted-foreground">Алгоритм</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="font-semibold text-lg">{product.powerConsumption}W</div>
                  <div className="text-sm text-muted-foreground">Потребление</div>
                </CardContent>
              </Card>
            </div>

            {/* Price */}
            <div className="flex items-center space-x-4">
              <span className="text-3xl font-bold text-primary">
                ${parseFloat(product.price).toLocaleString()}
              </span>
              {product.oldPrice && (
                <span className="text-xl text-muted-foreground line-through">
                  ${parseFloat(product.oldPrice).toLocaleString()}
                </span>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                onClick={handleAddToCart}
                disabled={isAdding || justAdded}
                className={`flex-1 ${justAdded ? 'bg-green-600 hover:bg-green-600' : 'btn-primary-green'}`}
                size="lg"
              >
                {isAdding ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Добавление...
                  </>
                ) : justAdded ? (
                  <>
                    <Check className="h-5 w-5 mr-2" />
                    Добавлено в корзину
                  </>
                ) : (
                  <>
                    <ShoppingCart className="h-5 w-5 mr-2" />
                    Купить
                  </>
                )}
              </Button>
              
              <Button variant="outline" size="lg">
                <Heart className="h-5 w-5 mr-2" />
                В избранное
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t">
              <div className="flex items-center space-x-2 text-sm">
                <Shield className="h-4 w-4 text-primary" />
                <span>Бесплатная доставка</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <Truck className="h-4 w-4 text-primary" />
                <span>Отправка в день заказа</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <Wrench className="h-4 w-4 text-primary" />
                <span>Гарантия на оборудование</span>
              </div>
            </div>
          </div>
        </div>

        {/* Product Details Tabs */}
        <div className="bg-white rounded-xl shadow-sm">
          <Tabs defaultValue="description" className="p-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="description">Описание</TabsTrigger>
              <TabsTrigger value="specifications">Характеристики</TabsTrigger>
            </TabsList>
            
            <TabsContent value="description" className="mt-6">
              <div className="prose max-w-none">
                <h3 className="text-xl font-semibold mb-4">Описание</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {product.description || `${product.name} — это мощный ASIC-майнер, разработанный для добычи криптовалют, работающих на алгоритме ${product.algorithm}. Основанный на современных чипах, этот майнер предлагает высокий хешрейт ${product.hashrate} при оптимальном энергопотреблении ${product.powerConsumption}W.`}
                </p>
                
                <h4 className="text-lg font-semibold mt-6 mb-3">Потребление электроэнергии</h4>
                <p className="text-muted-foreground">
                  Усовершенствованная система охлаждения для поддержания стабильной работы при высоких нагрузках, так как для оптимизации прибыли важна надежность настройки майнинга.
                </p>

                <h4 className="text-lg font-semibold mt-6 mb-3">Простота использования</h4>
                <p className="text-muted-foreground">
                  {product.name} предоставляет пользователю простую в использовании веб-интерфейс для профессионального майнинга с упором на высокую рентабельность и надежность.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="specifications" className="mt-6">
              <h3 className="text-xl font-semibold mb-4">Технические характеристики</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Хешрейт</span>
                    <span>{specifications.hashrate || product.hashrate}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Алгоритм</span>
                    <span>{specifications.algorithm || product.algorithm}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Потребляемая мощность</span>
                    <span>{specifications.powerConsumption || `${product.powerConsumption}W`}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Энергоэффективность</span>
                    <span>{specifications.powerEfficiency || 'Не указано'}</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Рабочая температура</span>
                    <span>{specifications.operatingTemperature || '0°C - 40°C'}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Сетевое подключение</span>
                    <span>{specifications.networkConnection || 'Ethernet'}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Размеры</span>
                    <span>{specifications.dimensions || 'Не указано'}</span>
                  </div>
                  <div className="flex justify-between border-b pb-2">
                    <span className="font-medium">Производитель</span>
                    <span>{product.brand}</span>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Recently Viewed Products Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Недавно смотрели</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {/* This would show recently viewed products in a real app */}
            <div className="text-center text-muted-foreground py-8 col-span-full">
              <p>История просмотров пуста</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
