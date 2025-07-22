import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { insertUserSchema, type InsertUser, type Order } from '@shared/schema';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { addAuthHeaders } from '@/lib/auth';
import { User, Package, Settings, Loader2, Eye } from 'lucide-react';

export default function Account() {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isUpdating, setIsUpdating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<InsertUser>({
    resolver: zodResolver(insertUserSchema.partial()),
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      country: user?.country || '',
      city: user?.city || '',
      address: user?.address || '',
    },
  });

  // Fetch user orders
  const { data: orders = [], isLoading: ordersLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: async () => {
      const response = await fetch('/api/orders', {
        headers: addAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch orders');
      return response.json();
    },
    enabled: isAuthenticated,
  });

  const updateProfileMutation = useMutation({
    mutationFn: async (data: Partial<InsertUser>) => {
      const response = await apiRequest('PUT', '/api/profile', data);
      return response.json();
    },
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(['auth', 'me'], updatedUser);
      toast({
        title: "Профиль обновлен",
        description: "Ваши данные успешно сохранены",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Ошибка обновления",
        description: error.message || "Не удалось обновить профиль",
        variant: "destructive",
      });
    },
  });

  const onSubmit = async (data: InsertUser) => {
    setIsUpdating(true);
    try {
      await updateProfileMutation.mutateAsync(data);
    } finally {
      setIsUpdating(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'pending':
        return 'secondary';
      case 'processing':
        return 'default';
      case 'shipped':
        return 'outline';
      case 'delivered':
        return 'default';
      default:
        return 'secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Ожидает оплаты';
      case 'processing':
        return 'В обработке';
      case 'shipped':
        return 'Отправлен';
      case 'delivered':
        return 'Доставлен';
      default:
        return status;
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Вход в личный кабинет</h1>
          <p className="text-muted-foreground mb-6">
            Войдите в систему для доступа к личному кабинету
          </p>
          <Button onClick={() => window.location.href = '/'}>
            Перейти на главную
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Личный кабинет</h1>
          <p className="text-muted-foreground">
            Управляйте своим профилем и отслеживайте заказы
          </p>
        </div>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-3">
            <TabsTrigger value="profile" className="flex items-center">
              <User className="h-4 w-4 mr-2" />
              Профиль
            </TabsTrigger>
            <TabsTrigger value="orders" className="flex items-center">
              <Package className="h-4 w-4 mr-2" />
              Мои заказы
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              Настройки
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Информация профиля</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Имя</Label>
                      <Input
                        id="name"
                        {...register('name')}
                        className={errors.name ? 'border-destructive' : ''}
                      />
                      {errors.name && (
                        <p className="text-sm text-destructive">{errors.name.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        {...register('email')}
                        className={errors.email ? 'border-destructive' : ''}
                      />
                      {errors.email && (
                        <p className="text-sm text-destructive">{errors.email.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="phone">Телефон</Label>
                      <Input
                        id="phone"
                        type="tel"
                        {...register('phone')}
                        className={errors.phone ? 'border-destructive' : ''}
                      />
                      {errors.phone && (
                        <p className="text-sm text-destructive">{errors.phone.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="country">Страна</Label>
                      <Input
                        id="country"
                        {...register('country')}
                        className={errors.country ? 'border-destructive' : ''}
                      />
                      {errors.country && (
                        <p className="text-sm text-destructive">{errors.country.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="city">Город</Label>
                      <Input
                        id="city"
                        {...register('city')}
                        className={errors.city ? 'border-destructive' : ''}
                      />
                      {errors.city && (
                        <p className="text-sm text-destructive">{errors.city.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="address">Адрес</Label>
                    <Input
                      id="address"
                      {...register('address')}
                      className={errors.address ? 'border-destructive' : ''}
                    />
                    {errors.address && (
                      <p className="text-sm text-destructive">{errors.address.message}</p>
                    )}
                  </div>

                  <Button type="submit" disabled={isUpdating} className="btn-primary-green">
                    {isUpdating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Сохранение...
                      </>
                    ) : (
                      'Сохранить изменения'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders">
            <Card>
              <CardHeader>
                <CardTitle>История заказов</CardTitle>
              </CardHeader>
              <CardContent>
                {ordersLoading ? (
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="border rounded-lg p-4 animate-pulse">
                        <div className="flex justify-between items-start mb-2">
                          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                          <div className="h-6 bg-gray-200 rounded w-20"></div>
                        </div>
                        <div className="h-3 bg-gray-200 rounded w-1/3 mb-2"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/6"></div>
                      </div>
                    ))}
                  </div>
                ) : orders.length === 0 ? (
                  <div className="text-center py-8">
                    <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">У вас пока нет заказов</p>
                    <Button className="mt-4" onClick={() => window.location.href = '/catalog'}>
                      Перейти к каталогу
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {orders.map((order: Order) => (
                      <div key={order.id} className="border rounded-lg p-4">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3">
                          <div>
                            <h3 className="font-semibold">Заказ #{order.id}</h3>
                            <p className="text-sm text-muted-foreground">
                              {new Date(order.createdAt!).toLocaleDateString('ru-RU', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                              })}
                            </p>
                          </div>
                          <Badge variant={getStatusBadgeVariant(order.status || 'pending')}>
                            {getStatusText(order.status || 'pending')}
                          </Badge>
                        </div>
                        
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
                          <div className="text-sm text-muted-foreground mb-2 sm:mb-0">
                            <p>Способ оплаты: {
                              order.paymentMethod === 'crypto' ? 'Криптовалюта' :
                              order.paymentMethod === 'bank' ? 'Банковский перевод' :
                              'Western Union / MoneyGram'
                            }</p>
                          </div>
                          <div className="flex items-center space-x-4">
                            <span className="font-semibold text-primary">
                              ${parseFloat(order.totalAmount).toLocaleString()}
                            </span>
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-2" />
                              Подробнее
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Настройки аккаунта</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Уведомления по email</h4>
                      <p className="text-sm text-muted-foreground">
                        Получать уведомления о статусе заказов
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Настроить
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Смена пароля</h4>
                      <p className="text-sm text-muted-foreground">
                        Обновить пароль для входа в систему
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Изменить
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Удалить аккаунт</h4>
                      <p className="text-sm text-muted-foreground">
                        Безвозвратно удалить ваш аккаунт и все данные
                      </p>
                    </div>
                    <Button variant="destructive" size="sm">
                      Удалить
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
