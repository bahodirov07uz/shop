import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb';
import ProductCard from '@/components/product/product-card';
import ProductFilters from '@/components/product/product-filters';
import { addAuthHeaders } from '@/lib/auth';
import type { Product } from '@shared/schema';

interface FilterState {
  brands: string[];
  algorithms: string[];
  priceRange: [number, number];
  hashrate: string;
  inStock: boolean;
}

const defaultFilters: FilterState = {
  brands: [],
  algorithms: [],
  priceRange: [500, 15000],
  hashrate: 'all',
  inStock: false,
};

export default function Catalog() {
  const [location] = useLocation();
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [sortBy, setSortBy] = useState('popular');
  const [searchQuery, setSearchQuery] = useState('');

  // Get search query from URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const search = urlParams.get('search');
    if (search) {
      setSearchQuery(search);
    }
  }, [location]);

  const { data: products = [], isLoading, error } = useQuery({
    queryKey: ['products', filters, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      
      if (filters.brands.length > 0) {
        filters.brands.forEach(brand => params.append('brand', brand));
      }
      if (filters.algorithms.length > 0) {
        filters.algorithms.forEach(algo => params.append('algorithm', algo));
      }
      if (filters.priceRange[0] > 500) {
        params.set('priceMin', filters.priceRange[0].toString());
      }
      if (filters.priceRange[1] < 15000) {
        params.set('priceMax', filters.priceRange[1].toString());
      }
      if (filters.inStock) {
        params.set('inStock', 'true');
      }

      const response = await fetch(`/api/products?${params.toString()}`, {
        headers: addAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch products');
      return response.json();
    },
  });

  // Filter and sort products
  const filteredProducts = products
    .filter((product: Product) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          product.name.toLowerCase().includes(query) ||
          product.brand.toLowerCase().includes(query) ||
          product.algorithm.toLowerCase().includes(query)
        );
      }
      return true;
    })
    .sort((a: Product, b: Product) => {
      switch (sortBy) {
        case 'price-asc':
          return parseFloat(a.price) - parseFloat(b.price);
        case 'price-desc':
          return parseFloat(b.price) - parseFloat(a.price);
        case 'hashrate':
          // Simple hashrate comparison (would need better parsing in real app)
          return b.hashrate.localeCompare(a.hashrate);
        default:
          return 0;
      }
    });

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  const handleResetFilters = () => {
    setFilters(defaultFilters);
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-destructive">Ошибка загрузки каталога</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Page Header */}
      <div className="bg-white border-b py-8">
        <div className="container mx-auto px-4">
          <Breadcrumb className="mb-4">
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Главная</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Каталог</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <h1 className="text-3xl font-bold">ASIC майнеры</h1>
          {searchQuery && (
            <p className="text-muted-foreground mt-2">
              Результаты поиска для: "{searchQuery}"
            </p>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Filters */}
          <div className="lg:col-span-1">
            <ProductFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onReset={handleResetFilters}
            />
          </div>

          {/* Products Grid */}
          <div className="lg:col-span-3">
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <p className="text-muted-foreground">
                {isLoading ? 'Загрузка...' : `Найдено ${filteredProducts.length} товаров`}
              </p>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full sm:w-auto">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popular">По популярности</SelectItem>
                  <SelectItem value="price-asc">Сначала дешевые</SelectItem>
                  <SelectItem value="price-desc">Сначала дорогие</SelectItem>
                  <SelectItem value="hashrate">По хешрейту</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Products Grid */}
            {isLoading ? (
              <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="bg-white rounded-xl p-4 animate-pulse">
                    <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg mb-4">
                  {searchQuery ? 'По вашему запросу ничего не найдено' : 'Товары не найдены'}
                </p>
                {(searchQuery || filters !== defaultFilters) && (
                  <Button onClick={() => {
                    setSearchQuery('');
                    handleResetFilters();
                    window.history.replaceState({}, '', '/catalog');
                  }}>
                    Сбросить фильтры
                  </Button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredProducts.map((product: Product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}

            {/* Pagination would go here in a real application */}
            {filteredProducts.length > 0 && (
              <div className="mt-12 flex justify-center">
                <div className="flex items-center space-x-2">
                  <Button variant="outline" disabled>
                    Предыдущая
                  </Button>
                  <Button variant="default" className="bg-primary">
                    1
                  </Button>
                  <Button variant="outline">2</Button>
                  <Button variant="outline">3</Button>
                  <Button variant="outline">
                    Следующая
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
