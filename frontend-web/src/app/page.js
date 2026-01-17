"use client";

import { useEffect, useState } from "react";
import api from "./lib/api";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function HomePage() {
  const router = useRouter();
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) router.push("/login");
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    const token = localStorage.getItem("access");

    const res = await api.get("home/", {
      headers: { Authorization: `Bearer ${token}` },
    });

    setProducts(res.data);
  };

  return (
  <div className="page-bg">
    <div className="card animate-card home-card w-full">
      
      {/* HERO */}
      <section className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-slate-900">
          Welcome to <span className="text-[rgb(var(--brand))]">Cartsy</span>
        </h1>

        <p className="mt-2 text-slate-500 text-sm">
          Your one-stop shop for everything you love 💙
        </p>

        <button
          onClick={() => router.push("/products")}
          className="btn btn-primary mt-6 px-6 py-3 rounded-full shadow-lg"
        >
          🛒 Start Shopping
        </button>
      </section>

      {/* FEATURED */}
      <section className="home-section">
        <h2 className="section-title">Featured Products</h2>

        <div className="product-grid">
          {products.map((p) => (
            <div key={p.id} className="product-card">
              <Image
                src={`http://127.0.0.1:8000${p.image}`}
                alt={`${p.product_name}`}
                width={400}
                height={260}
                className="product-img"
                priority
                unoptimized
              />
 
              <h5 className="mt-3 font-semibold text-slate-800">
                {p.product_name}
              </h5>

              <p className="price">₹{p.price}</p>

              <button
                className="secondary-btn"
                onClick={() => router.push(`/product/${p.id}`)}
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      </section>

    </div>
  </div>
);
}