'use client'

import { useCart } from '@/context/CartContext'
import type { Product } from '@/lib/products'

interface Props {
  product: Product
  className?: string
  quantity?: number
}

export default function AddToCartButton({ product, className = '', quantity = 1 }: Props) {
  const { addItem } = useCart()

  if (!product.inStock) {
    return (
      <button
        disabled
        className={`btn-ghost opacity-40 cursor-not-allowed py-2.5 rounded-sm text-xs tracking-widest uppercase ${className}`}
      >
        Out of Stock
      </button>
    )
  }

  return (
    <button
      onClick={() =>
        addItem({
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.images[0],
          quantity,
          department: product.department,
        })
      }
      className={`btn-burgundy py-2.5 rounded-sm text-xs tracking-widest uppercase ${className}`}
    >
      Add to Cart
    </button>
  )
}
