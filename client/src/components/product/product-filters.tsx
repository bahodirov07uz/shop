import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Filter, X } from 'lucide-react';

interface FilterState {
  brands: string[];
  algorithms: string[];
  priceRange: [number, number];
  hashrate: string;
  inStock: boolean;
}

interface ProductFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onReset: () => void;
}

export default function ProductFilters({ filters, onFiltersChange, onReset }: ProductFiltersProps) {
  const brands = ['Bitmain', 'MicroBT', 'Canaan', 'Avalon'];
  const algorithms = ['SHA-256', 'Scrypt', 'Ethash', 'X11'];

  const handleBrandChange = (brand: string, checked: boolean) => {
    const newBrands = checked
      ? [...filters.brands, brand]
      : filters.brands.filter(b => b !== brand);
    
    onFiltersChange({ ...filters, brands: newBrands });
  };

  const handleAlgorithmChange = (algorithm: string, checked: boolean) => {
    const newAlgorithms = checked
      ? [...filters.algorithms, algorithm]
      : filters.algorithms.filter(a => a !== algorithm);
    
    onFiltersChange({ ...filters, algorithms: newAlgorithms });
  };

  const handlePriceRangeChange = (range: [number, number]) => {
    onFiltersChange({ ...filters, priceRange: range });
  };

  const handleHashrateChange = (hashrate: string) => {
    onFiltersChange({ ...filters, hashrate });
  };

  const handleInStockChange = (inStock: boolean) => {
    onFiltersChange({ ...filters, inStock });
  };

  const hasActiveFilters = filters.brands.length > 0 || 
                          filters.algorithms.length > 0 || 
                          filters.priceRange[0] > 500 || 
                          filters.priceRange[1] < 15000 ||
                          filters.hashrate !== 'all' ||
                          filters.inStock;

  return (
    <Card className="sidebar-filter">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg">
            <Filter className="h-5 w-5 mr-2" />
            Фильтры
          </CardTitle>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              className="text-xs"
            >
              <X className="h-3 w-3 mr-1" />
              Сбросить
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Производитель */}
        <div>
          <h6 className="font-semibold text-sm mb-3">Производитель</h6>
          <div className="space-y-2">
            {brands.map((brand) => (
              <div key={brand} className="flex items-center space-x-2">
                <Checkbox
                  id={`brand-${brand}`}
                  checked={filters.brands.includes(brand)}
                  onCheckedChange={(checked) => 
                    handleBrandChange(brand, checked as boolean)
                  }
                />
                <label 
                  htmlFor={`brand-${brand}`} 
                  className="text-sm cursor-pointer"
                >
                  {brand}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Алгоритм */}
        <div>
          <h6 className="font-semibold text-sm mb-3">Алгоритм</h6>
          <div className="space-y-2">
            {algorithms.map((algorithm) => (
              <div key={algorithm} className="flex items-center space-x-2">
                <Checkbox
                  id={`algo-${algorithm}`}
                  checked={filters.algorithms.includes(algorithm)}
                  onCheckedChange={(checked) => 
                    handleAlgorithmChange(algorithm, checked as boolean)
                  }
                />
                <label 
                  htmlFor={`algo-${algorithm}`} 
                  className="text-sm cursor-pointer"
                >
                  {algorithm}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Цена */}
        <div>
          <h6 className="font-semibold text-sm mb-3">Цена, $</h6>
          <div className="space-y-3">
            <Slider
              value={filters.priceRange}
              onValueChange={handlePriceRangeChange}
              max={15000}
              min={500}
              step={100}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>${filters.priceRange[0].toLocaleString()}</span>
              <span>${filters.priceRange[1].toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Хешрейт */}
        <div>
          <h6 className="font-semibold text-sm mb-3">Хешрейт</h6>
          <Select value={filters.hashrate} onValueChange={handleHashrateChange}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все</SelectItem>
              <SelectItem value="low">До 50 TH/s</SelectItem>
              <SelectItem value="medium">50-100 TH/s</SelectItem>
              <SelectItem value="high">100+ TH/s</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* В наличии */}
        <div className="flex items-center space-x-2">
          <Checkbox
            id="in-stock"
            checked={filters.inStock}
            onCheckedChange={(checked) => handleInStockChange(checked as boolean)}
          />
          <label htmlFor="in-stock" className="text-sm cursor-pointer">
            Только в наличии
          </label>
        </div>
      </CardContent>
    </Card>
  );
}
