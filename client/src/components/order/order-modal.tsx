import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { insertOrderSchema, type InsertOrder } from '@shared/schema';
import { useCart } from '@/hooks/use-cart';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { ShoppingBag, CreditCard, Bitcoin, University, Loader2, Lock } from 'lucide-react';

interface OrderModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function OrderModal({ isOpen, onClose }: OrderModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { cartItems, cartTotal, clearCart } = useCart();
  const { user } = useAuth();
  const { toast } = useToast();

  const shippingCost = 50;
  const processingFee = Math.round(cartTotal * 0.01); // 1% processing fee
  const totalAmount = cartTotal + shippingCost + processingFee;

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset,
  } = useForm<InsertOrder & { comment?: string; terms: boolean }>({
    resolver: zodResolver(
      insertOrderSchema.extend({
        comment: insertOrderSchema.shape.comment.optional(),
        terms: insertOrderSchema.shape.comment.transform(() => true),
      })
    ),
    defaultValues: {
      email: user?.email || '',
      name: user?.name || '',
      phone: user?.phone || '',
      country: user?.country || '',
      city: user?.city || '',
      address: user?.address || '',
      paymentMethod: 'crypto',
      totalAmount: totalAmount.toString(),
    },
  });

  const paymentMethod = watch('paymentMethod');

  const onSubmit = async (data: InsertOrder & { comment?: string; terms: boolean }) => {
    if (cartItems.length === 0) {
      toast({
        title: "Ошибка",
        description: "Корзина пуста",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiRequest('POST', '/api/orders', {
        ...data,
        totalAmount: totalAmount.toString(),
      });
      
      await clearCart();
      
      toast({
        title: "Заказ оформлен",
        description: "Ваш заказ принят в обработку. В ближайшее время с вами свяжется менеджер.",
      });
      
      reset();
      onClose();
    } catch (error: any) {
      toast({
        title: "Ошибка оформления заказа",
        description: error.message || "Произошла ошибка при оформлении заказа",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getPaymentIcon = (method: string) => {
    switch (method) {
      case 'crypto':
        return <Bitcoin className="h-4 w-4" />;
      case 'bank':
        return <University className="h-4 w-4" />;
      case 'wire':
        return <CreditCard className="h-4 w-4" />;
      default:
        return <CreditCard className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <ShoppingBag className="h-5 w-5 mr-2" />
            Оформление заказа
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Contact Information */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg mb-4">Контактная информация</h3>
              
              <div className="space-y-2">
                <Label htmlFor="name">Имя *</Label>
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
                <Label htmlFor="email">Email *</Label>
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
                <Label htmlFor="phone">Телефон *</Label>
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
                <Label htmlFor="country">Страна *</Label>
                <Select onValueChange={(value) => setValue('country', value)} defaultValue={watch('country')}>
                  <SelectTrigger className={errors.country ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Выберите страну" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Russia">Россия</SelectItem>
                    <SelectItem value="Ukraine">Украина</SelectItem>
                    <SelectItem value="Kazakhstan">Казахстан</SelectItem>
                    <SelectItem value="Belarus">Беларусь</SelectItem>
                    <SelectItem value="Other">Другая</SelectItem>
                  </SelectContent>
                </Select>
                {errors.country && (
                  <p className="text-sm text-destructive">{errors.country.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="city">Город *</Label>
                <Input
                  id="city"
                  {...register('city')}
                  className={errors.city ? 'border-destructive' : ''}
                />
                {errors.city && (
                  <p className="text-sm text-destructive">{errors.city.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">Адрес доставки *</Label>
                <Textarea
                  id="address"
                  {...register('address')}
                  placeholder="Укажите полный адрес для доставки"
                  className={errors.address ? 'border-destructive' : ''}
                  rows={3}
                />
                {errors.address && (
                  <p className="text-sm text-destructive">{errors.address.message}</p>
                )}
              </div>
            </div>

            {/* Order Summary and Payment */}
            <div className="space-y-6">
              {/* Payment Method */}
              <div>
                <h3 className="font-semibold text-lg mb-4">Способ оплаты</h3>
                <RadioGroup
                  value={paymentMethod}
                  onValueChange={(value) => setValue('paymentMethod', value)}
                  className="space-y-3"
                >
                  <div className="flex items-center space-x-2 p-3 border rounded-lg">
                    <RadioGroupItem value="crypto" id="crypto" />
                    <Label htmlFor="crypto" className="flex items-center cursor-pointer">
                      <Bitcoin className="h-4 w-4 text-yellow-500 mr-2" />
                      Криптовалюта (Bitcoin, USDT)
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 border rounded-lg">
                    <RadioGroupItem value="bank" id="bank" />
                    <Label htmlFor="bank" className="flex items-center cursor-pointer">
                      <University className="h-4 w-4 text-blue-500 mr-2" />
                      Банковский перевод
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 border rounded-lg">
                    <RadioGroupItem value="wire" id="wire" />
                    <Label htmlFor="wire" className="flex items-center cursor-pointer">
                      <CreditCard className="h-4 w-4 text-green-500 mr-2" />
                      Western Union / MoneyGram
                    </Label>
                  </div>
                </RadioGroup>

                <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700 flex items-center">
                    <Lock className="h-4 w-4 mr-2" />
                    Обработка заказа через платежную систему Cryptadium. Комиссия за транзакцию включена в стоимость.
                  </p>
                </div>
              </div>

              {/* Order Summary */}
              <div>
                <h3 className="font-semibold text-lg mb-4">Ваш заказ</h3>
                <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                  {cartItems.map((item) => (
                    <div key={item.id} className="flex justify-between items-center text-sm">
                      <div className="flex-1">
                        <span className="font-medium">{item.product.name}</span>
                        <span className="text-muted-foreground"> × {item.quantity}</span>
                      </div>
                      <span className="font-medium">
                        ${(parseFloat(item.product.price) * item.quantity).toLocaleString()}
                      </span>
                    </div>
                  ))}
                  
                  <hr />
                  
                  <div className="flex justify-between text-sm">
                    <span>Доставка</span>
                    <span>${shippingCost}</span>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span>Комиссия платежной системы</span>
                    <span>${processingFee}</span>
                  </div>
                  
                  <hr />
                  
                  <div className="flex justify-between font-semibold text-lg text-primary">
                    <span>Итого к оплате:</span>
                    <span>${totalAmount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Comment */}
              <div className="space-y-2">
                <Label htmlFor="comment">Комментарий к заказу</Label>
                <Textarea
                  id="comment"
                  {...register('comment')}
                  placeholder="Дополнительные пожелания или инструкции по доставке"
                  rows={3}
                />
              </div>

              {/* Terms Agreement */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="terms"
                  {...register('terms')}
                  required
                />
                <Label htmlFor="terms" className="text-sm">
                  Согласен с{' '}
                  <a href="#" className="text-primary hover:underline">
                    условиями продажи
                  </a>
                  {' '}и{' '}
                  <a href="#" className="text-primary hover:underline">
                    политикой конфиденциальности
                  </a>
                  {' '}*
                </Label>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading || cartItems.length === 0}
                className="w-full btn-primary-green text-lg py-3"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Обработка заказа...
                  </>
                ) : (
                  <>
                    <Lock className="h-5 w-5 mr-2" />
                    Оформить заказ
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
