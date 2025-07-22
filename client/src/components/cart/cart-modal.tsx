import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react';
import { useCart } from '@/hooks/use-cart';
import { useToast } from '@/hooks/use-toast';
import OrderModal from '@/components/order/order-modal';

interface CartModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CartModal({ isOpen, onClose }: CartModalProps) {
  const [showOrderModal, setShowOrderModal] = useState(false);
  const { cartItems, updateCartItem, removeFromCart, cartTotal, cartCount } = useCart();
  const { toast } = useToast();

  const handleQuantityChange = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    try {
      await updateCartItem(itemId, newQuantity);
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось обновить количество",
        variant: "destructive",
      });
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    try {
      await removeFromCart(itemId);
      toast({
        title: "Товар удален",
        description: "Товар удален из корзины",
      });
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось удалить товар",
        variant: "destructive",
      });
    }
  };

  const shippingCost = 50;
  const totalWithShipping = cartTotal + shippingCost;

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <ShoppingBag className="h-5 w-5 mr-2" />
              Корзина ({cartCount})
            </DialogTitle>
          </DialogHeader>

          {cartItems.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingBag className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Корзина пуста</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="max-h-96 overflow-y-auto space-y-4 pr-2">
                {cartItems.map((item) => (
                  <div key={item.id} className="cart-item">
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 flex-shrink-0">
                        <img
                          src={item.product.imageUrl}
                          alt={item.product.name}
                          className="w-full h-full object-cover rounded"
                        />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h6 className="font-medium text-sm line-clamp-2">
                          {item.product.name}
                        </h6>
                        <p className="text-xs text-muted-foreground">
                          {item.product.algorithm}, {item.product.powerConsumption}W
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                          disabled={item.quantity <= 1}
                        >
                          <Minus className="h-3 w-3" />
                        </Button>
                        
                        <Input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => {
                            const qty = parseInt(e.target.value);
                            if (qty > 0) handleQuantityChange(item.id, qty);
                          }}
                          className="w-16 h-8 text-center text-sm"
                          min="1"
                        />
                        
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                      
                      <div className="text-right min-w-[80px]">
                        <div className="font-semibold text-primary">
                          ${(parseFloat(item.product.price) * item.quantity).toLocaleString()}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveItem(item.id)}
                          className="text-destructive hover:text-destructive p-1 h-auto"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Cart Summary */}
              <div className="border-t pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Подытог:</span>
                  <span>${cartTotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Доставка:</span>
                  <span>${shippingCost}</span>
                </div>
                <div className="flex justify-between font-semibold text-lg border-t pt-2">
                  <span>Итого:</span>
                  <span className="text-primary">${totalWithShipping.toLocaleString()}</span>
                </div>
              </div>

              {/* Checkout Button */}
              <Button
                onClick={() => {
                  setShowOrderModal(true);
                  onClose();
                }}
                className="w-full btn-primary-green"
              >
                Оформить заказ
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <OrderModal
        isOpen={showOrderModal}
        onClose={() => setShowOrderModal(false)}
      />
    </>
  );
}
