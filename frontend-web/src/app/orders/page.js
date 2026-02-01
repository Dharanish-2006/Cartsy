"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../lib/api";

export default function OrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access");
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await api.get("orders/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setOrders(res.data);
    } finally {
      setLoading(false);
    }
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
          <span
            className="logo cursor-pointer"
            onClick={() => router.push("/")}
          >
            Cartsy
          </span>

          <div className="nav-actions">
            <button onClick={() => router.push("/cart")}>Cart</button>
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
        <div className="card home-card">
          <h1 className="text-3xl font-extrabold mb-8">My Orders</h1>

          {orders.length === 0 && (
            <div className="text-center py-12">
              <p className="text-slate-500 mb-4">
                You haven't placed any orders yet.
              </p>
              <button
                className="btn btn-primary px-6 py-3"
                onClick={() => router.push("/")}
              >
                🛍 Start Shopping
              </button>
            </div>
          )}

          <div className="space-y-8">
            {orders.map((order) => (
              <div
                key={order.id}
                className="border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition"
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <p className="font-semibold">
                      Order #{order.id}
                    </p>
                    <p className="text-sm text-slate-500">
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <span
                    className={`px-4 py-1 rounded-full text-sm font-semibold
                      ${
                        order.status === "Delivered"
                          ? "bg-green-100 text-green-700"
                          : order.status === "Cancelled"
                          ? "bg-red-100 text-red-700"
                          : "bg-yellow-100 text-yellow-700"
                      }
                    `}
                  >
                    {order.status}
                  </span>
                </div>

                <div className="mt-6 space-y-3">
                  {order.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between text-sm"
                    >
                      <span>
                        {item.product_name} × {item.quantity}
                      </span>
                      <span className="font-medium">
                        ₹{item.price * item.quantity}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span className="text-[rgb(var(--brand))]">
                    ₹
                    {order.items.reduce(
                      (sum, i) => sum + i.price * i.quantity,
                      0
                    )}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
