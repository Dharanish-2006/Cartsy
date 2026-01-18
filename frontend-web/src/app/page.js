"use client";

import { useEffect, useState } from "react";
import api from "./lib/api";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) router.push("/login");
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    const res = await api.get("home/");
    setProducts(res.data);
  };

  return (
    <div className="home-bg">
      <section className="hero">
        <h1>
          Welcome to <span>Cartsy</span>
        </h1>
        <p>Your one-stop shop for everything you love 💙</p>
        <button onClick={() => router.push("/products")}>
          🛒 Start Shopping
        </button>
      </section>
      <section className="section">
        <h2>Featured Products</h2>

        <div className="grid">
          {products.map((p) => (
            <div key={p.id} className="card">
              <img src={p.image} />
              <h5>{p.product_name}</h5>
              <p>₹{p.price}</p>
              <button onClick={() => router.push(`/product/${p.id}`)}>
                View Details
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
