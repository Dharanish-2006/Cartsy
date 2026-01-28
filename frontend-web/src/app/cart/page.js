"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../lib/api";
import Image from "next/image";

export default function CartPage() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) router.push("/login");
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await api.get("cart/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setItems(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  const updateQty = async (itemId, action) => {
    const token = localStorage.getItem("access");
    await api.post(
      "cart/update/",
      { item_id: itemId, action },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    fetchCart();
  };

  if (loading) {
    return (
      <div className="page-bg">
        <div className="card home-card skeleton-detail" />
      </div>
    );
  }

  return (
    <div className="page-bg">
      <div className="navbar">
        <div className="navbar-inner">
          <span className="logo cursor-pointer" onClick={() => router.push("/")}>
            Cartsy
          </span>

          <div className="nav-actions">
            <button onClick={() => router.push("/orders")}>Orders</button>
            <button
              className="logout"
              onClick={() => {
                localStorage.clear();
                router.push("/login");
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="home-wrapper">
        <div className="card animate-card home-card">
          <h1 className="text-2xl font-extrabold mb-6">Your Cart</h1>

          {items.length === 0 ? (
            <p className="text-center text-slate-500">
              Your cart is empty 🛒
            </p>
          ) : (
            <div className="space-y-5">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-4 p-4 rounded-xl bg-slate-50"
                >
                  <Image
                    src={`https://cartsy-ht0x.onrender.com/${item.product.image}`}
                    alt={item.product.product_name}
                    width={90}
                    height={90}
                    unoptimized
                    className="rounded-lg object-cover"
                  />

                  <div className="flex-1">
                    <h3 className="font-semibold">
                      {item.product.product_name}
                    </h3>
                    <p className="text-sm text-slate-500">
                      ₹{item.product.price}
                    </p>
                  </div>

                  <div className="qty-control">
                    <button onClick={() => updateQty(item.id, "decrease")}>
                      −
                    </button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQty(item.id, "increase")}>
                      +
                    </button>
                  </div>
                </div>
              ))}

              <div className="flex justify-between items-center border-t pt-6 mt-6">
                <span className="font-semibold text-lg">Total</span>
                <span className="text-xl font-extrabold text-[rgb(var(--brand))]">
                  ₹{total}
                </span>
              </div>

              <button
                className="btn btn-primary w-full mt-4 py-3"
                onClick={() => router.push("/checkout")}
              >
                Proceed to Checkout
              </button>
            </div>
          )}
        </div>
      </div>

      {items.length > 0 && (
        <div className="mobile-sticky-cart">
          <div className="mobile-cart-inner">
            <span className="mobile-price">₹{total}</span>
            <button
              className="btn btn-primary"
              onClick={() => router.push("/checkout")}
            >
              Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
