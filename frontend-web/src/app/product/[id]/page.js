"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import api from "../../lib/api";
import Image from "next/image";

export default function ProductDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [product, setProduct] = useState(null);
  const [images, setImages] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [qty, setQty] = useState(1);
  const [zooming, setZooming] = useState(false);
  const [zoomPos, setZoomPos] = useState({ x: 50, y: 50 });
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const startX = useRef(0);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) router.push("/login");
    fetchProduct();
  }, []);

  const fetchProduct = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await api.get(`/products/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const imgs = [
        res.data.image,
        ...(res.data.images?.map((i) => i.image) || []),
      ];

      setProduct(res.data);
      setImages(imgs);
      setActiveIndex(0);
    } catch {
      router.push("/");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "ArrowRight" && activeIndex < images.length - 1)
        setActiveIndex((i) => i + 1);
      if (e.key === "ArrowLeft" && activeIndex > 0)
        setActiveIndex((i) => i - 1);
      if (e.key === "Escape") setLightboxOpen(false);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [activeIndex, images.length]);

  const onTouchStart = (e) => {
    startX.current = e.touches[0].clientX;
  };

  const onTouchEnd = (e) => {
    const diff = startX.current - e.changedTouches[0].clientX;
    if (diff > 50 && activeIndex < images.length - 1)
      setActiveIndex((i) => i + 1);
    if (diff < -50 && activeIndex > 0) setActiveIndex((i) => i - 1);
  };

  const addToCart = async () => {
    const token = localStorage.getItem("access");
    await api.post(
      "cart/",
      { product_id: product.id, quantity: qty },
      { headers: { Authorization: `Bearer ${token}` } },
    );
    router.push("/cart");
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
        <div className="card animate-card home-card product-detail-grid">
          <div className="flex flex-col">
            <div
              className="relative w-full h-[420px] overflow-hidden rounded-xl bg-gray-100 cursor-zoom-in"
              onMouseMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                setZoomPos({
                  x: ((e.clientX - rect.left) / rect.width) * 100,
                  y: ((e.clientY - rect.top) / rect.height) * 100,
                });
                setZooming(true);
              }}
              onMouseLeave={() => setZooming(false)}
              onClick={() => setLightboxOpen(true)}
              onTouchStart={onTouchStart}
              onTouchEnd={onTouchEnd}
            >
              <Image
                src={`http://127.0.0.1:8000${images[activeIndex]}`}
                alt={product.product_name}
                fill
                priority
                unoptimized
                className="object-cover transition-transform duration-300"
              />

              {zooming && (
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: `url(http://127.0.0.1:8000${images[activeIndex]})`,
                    backgroundPosition: `${zoomPos.x}% ${zoomPos.y}%`,
                    backgroundSize: "200%",
                  }}
                />
              )}
            </div>

            <div className="flex gap-3 mt-4 overflow-x-auto scrollbar-hide">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveIndex(idx)}
                  className={`border rounded-lg p-1 transition ${
                    idx === activeIndex
                      ? "border-[rgb(var(--brand))]"
                      : "border-gray-200"
                  }`}
                >
                  <Image
                    src={`http://127.0.0.1:8000${img}`}
                    alt="thumb"
                    width={80}
                    height={80}
                    loading="lazy"
                    unoptimized
                    className="rounded-md object-cover"
                  />
                </button>
              ))}
            </div>
          </div>

          <div className="product-info">
            <h1 className="text-3xl font-extrabold text-slate-900">
              {product.product_name}
            </h1>

            <p className="mt-3 text-slate-500 text-sm">
              {product.description || "High quality product with best pricing."}
            </p>

            <p className="text-2xl font-bold mt-6 text-[rgb(var(--brand))]">
              ₹{product.price}
            </p>

            <div className="qty-control">
              <button onClick={() => setQty(Math.max(1, qty - 1))}>−</button>
              <span>{qty}</span>
              <button onClick={() => setQty(qty + 1)}>+</button>
            </div>

            <button
              className="btn btn-primary w-full mt-6 py-3"
              onClick={addToCart}
            >
              🛒 Add to Cart
            </button>

            <button
              className="secondary-btn mt-3"
              onClick={() => router.push("/")}
            >
              ← Back to Shop
            </button>
          </div>
        </div>
      </div>

      <div className="mobile-sticky-cart">
        <div className="mobile-cart-inner">
          <span className="mobile-price">₹{product.price}</span>
          <button className="btn btn-primary" onClick={addToCart}>
            🛒 Add to Cart
          </button>
        </div>
      </div>

      {lightboxOpen && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
          onClick={() => setLightboxOpen(false)}
        >
          <Image
            src={`http://127.0.0.1:8000${images[activeIndex]}`}
            alt="fullscreen"
            width={1000}
            height={800}
            unoptimized
            className="rounded-xl"
          />
        </div>
      )}
    </div>
  );
}
