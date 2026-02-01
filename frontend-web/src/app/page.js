"use client";

import { useEffect, useState } from "react";
import api from "./lib/api";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function HomePage() {
  const router = useRouter();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await api.get("home/");
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    document.cookie = "access=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "refresh=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

    router.push("/login");
  };

  const SkeletonCard = () => (
    <div className="product-card skeleton">
      <div className="skeleton-img" />
      <div className="skeleton-text short" />
      <div className="skeleton-text" />
      <div className="skeleton-btn" />
    </div>
  );

  return (
    <div className="page-bg">
      {/* NAVBAR */}
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
            <button className="logout" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </div>
      <div className="home-wrapper">
        <div className="card animate-card home-card w-full">
          {/* HERO */}
          <section className="text-center mb-10">
            <h1 className="hero-title text-4xl font-extrabold text-slate-900">
              Welcome to{" "}
              <span className="text-[rgb(var(--brand))]">Cartsy</span>
            </h1>

            <p className="mt-3 text-slate-500 text-base max-w-md mx-auto">
              Your one-stop shop for everything you love 💙
            </p>

            <button
              onClick={() => router.push("/products")}
              className="btn btn-primary mt-6 px-6 py-3 rounded-full shadow-lg"
            >
              🛒 Start Shopping
            </button>
          </section>

          {/* PRODUCTS */}
          <section className="home-section">
            <h2 className="section-title">Featured Products</h2>

            <div className="product-grid">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <SkeletonCard key={i} />
                  ))
                : products.map((p) => (
                    <div key={p.id} className="product-card">
                      <Image
                        src={`https://cartsy-ht0x.onrender.com${p.image}`}
                        alt={`${p.product_name}`}
                        width={400}
                        height={260}
                        className="product-img"
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
    </div>
  );
}
