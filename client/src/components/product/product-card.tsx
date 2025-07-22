import { useState } from 'react';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShoppingCart, Check } from 'lucide-react';
import { useCart } from '@/hooks/use-cart';
import { useToast } from '@/hooks/use-toast';
import type { Product } from '@shared/schema';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const { addToCart } = useCart();
  const { toast } = useToast();

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isAdding || justAdded) return;
    
    setIsAdding(true);
    
    try {
      await addToCart(product.id, 1);
      setJustAdded(true);
      toast({
        title: "Товар добавлен в корзину",
        description: `${product.name} успешно добавлен в корзину`,
      });
      
      setTimeout(() => setJustAdded(false), 2000);
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

  const specifications = product.specifications ? JSON.parse(product.specifications) : {};

  return (
    <div className="product-card h-full">
      <Link href={`/product/${product.id}`}>
        <div className="cursor-pointer">
          <div className="relative h-48 overflow-hidden">
            {product.badge && (
              <Badge className={`product-badge ${product.badge}`}>
                {product.badge === 'sale' && '-20%'}
                {product.badge === 'new' && 'Новинка'}
              </Badge>
            )}
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              loading="lazy"
            />
          </div>
          
          <div className="p-4">
            <h5 className="font-semibold text-sm mb-2 line-clamp-2 min-h-[2.5rem]">
              {product.name}
            </h5>
            
            <div className="text-xs text-muted-foreground mb-3 space-y-1">
              <div>Хешрейт: {product.hashrate}</div>
              <div>Алгоритм: {product.algorithm}</div>
              <div>Энергопотребление: {product.powerConsumption}W</div>
            </div>
            
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="price-current text-lg font-bold">
                  ${parseFloat(product.price).toLocaleString()}
                </span>
                {product.oldPrice && (
                  <span className="price-old text-sm">
                    ${parseFloat(product.oldPrice).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </Link>
      
      <div className="px-4 pb-4">
        <Button
          onClick={handleAddToCart}
          disabled={isAdding || justAdded}
          className={`w-full transition-all duration-300 ${
            justAdded 
              ? 'bg-green-600 hover:bg-green-600' 
              : 'btn-primary-green'
          }`}
        >
          {isAdding ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Добавление...
            </>
          ) : justAdded ? (
            <>
              <Check className="h-4 w-4 mr-2" />
              Добавлено
            </>
          ) : (
            <>
              <ShoppingCart className="h-4 w-4 mr-2" />
              В корзину
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
