'use client'

import { useEffect } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useCart } from '@/context/CartContext'

export default function CartDrawer() {
  const { items, isOpen, closeCart, removeItem, updateQty, subtotal, itemCount } = useCart()

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  const handleCheckout = async () => {
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items }),
      })
      const { url } = await res.json()
      if (url) window.location.href = url
    } catch (err) {
      console.error('Checkout error:', err)
    }
  }

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity"
          onClick={closeCart}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <aside
        className={`fixed top-0 right-0 h-full w-full max-w-md bg-mahogany-light z-50 flex flex-col shadow-2xl border-l border-gold/20 transition-transform duration-350 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        aria-label="Shopping cart"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gold/20 bg-mahogany-dark">
          <div>
            <h2 className="font-playfair font-bold text-parchment text-lg tracking-wide">Your Cart</h2>
            <p className="text-xs text-gold/60 font-lora mt-0.5">{itemCount} {itemCount === 1 ? 'item' : 'items'}</p>
          </div>
          <button
            onClick={closeCart}
            className="p-2 text-parchment/50 hover:text-gold transition-colors"
            aria-label="Close cart"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Items */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="text-gold/20 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <p className="font-playfair text-parchment/60 text-lg mb-2">Your cart is empty</p>
              <p className="font-lora text-parchment/40 text-sm mb-6">Explore our collection of fine pipes and tobaccos</p>
              <button
                onClick={closeCart}
                className="btn-gold px-6 py-2.5 rounded-sm text-sm"
              >
                Browse the Shop
              </button>
            </div>
          ) : (
            items.map((item) => (
              <div key={item.id} className="flex gap-4 p-3 bg-mahogany/40 rounded-sm border border-gold/10 gold-frame">
                <div className="relative w-20 h-20 flex-shrink-0 rounded-sm overflow-hidden bg-mahogany-dark">
                  <Image
                    src={item.image}
                    alt={item.name}
                    fill
                    className="object-cover"
                    sizes="80px"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-playfair font-semibold text-parchment text-sm leading-snug line-clamp-2">{item.name}</p>
                  <p className="text-gold text-sm font-lora mt-1">${item.price.toFixed(2)}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <div className="flex items-center border border-gold/30 rounded-sm overflow-hidden">
                      <button
                        onClick={() => item.quantity > 1 ? updateQty(item.id, item.quantity - 1) : removeItem(item.id)}
                        className="px-2.5 py-1 text-parchment/60 hover:text-gold hover:bg-gold/10 transition-colors text-sm"
                      >
                        −
                      </button>
                      <span className="px-2.5 py-1 text-parchment text-sm font-lora border-x border-gold/20 min-w-[2rem] text-center">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQty(item.id, item.quantity + 1)}
                        className="px-2.5 py-1 text-parchment/60 hover:text-gold hover:bg-gold/10 transition-colors text-sm"
                      >
                        +
                      </button>
                    </div>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-xs text-parchment/30 hover:text-red-400 transition-colors font-lora"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="border-t border-gold/20 px-6 py-5 bg-mahogany-dark space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-lora text-parchment/70 text-sm">Subtotal</span>
              <span className="font-playfair font-bold text-gold text-lg">${subtotal.toFixed(2)}</span>
            </div>
            <p className="text-xs text-parchment/40 font-lora">Shipping & taxes calculated at checkout. Age verification required.</p>
            <button
              onClick={handleCheckout}
              className="btn-gold w-full py-3.5 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
            >
              Proceed to Checkout
            </button>
            <button
              onClick={closeCart}
              className="btn-ghost w-full py-2.5 rounded-sm font-lora text-sm"
            >
              Continue Shopping
            </button>
          </div>
        )}
      </aside>
    </>
  )
}
