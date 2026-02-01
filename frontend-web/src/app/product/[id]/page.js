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
    fetchProduct();
  }, []);

  const fetchProduct = async () => {
    try {
      const res = await api.get(`products/${id}/`);

      const imgs = [
        res.data.image,
        ...(res.data.images?.map((i) => i.image) || []),
      ];

      setProduct(res.data);
      setImages(imgs);
      setActiveIndex(0);
    } catch (err) {
      router.push("/");
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async () => {
    await api.post("cart/", {
      product_id: product.id,
      quantity: qty,
    });

    router.push("/cart");
  };

  const onTouchStart = (e) => {
    startX.current = e.touches[0].clientX;
  };

  const onTouchEnd = (e) => {
    const diff = startX.current - e.changedTouches[0].clientX;
    if (diff > 50 && activeIndex < images.length - 1)
      setActiveIndex((i) => i + 1);
    if (diff < -50 && activeIndex > 0)
      setActiveIndex((i) => i - 1);
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
            <button onClick={() => router.push("/cart")}>Cart</button>
            <button onClick={() => router.push("/orders")}>Orders</button>

            <button
              className="logout"
              onClick={async () => {
                await api.post("logout/");
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
          {/* IMAGE SECTION */}
          <div className="flex flex-col">
            <div
              className="relative w-full h-105 overflow-hidden rounded-xl bg-gray-100 cursor-zoom-in"
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
                src={`https://cartsy-ht0x.onrender.com${images[activeIndex]}`}
                alt={product.product_name}
                fill
                priority
                unoptimized
                className="object-cover"
              />

              {zooming && (
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: `url(https://cartsy-ht0x.onrender.com${images[activeIndex]})`,
                    backgroundPosition: `${zoomPos.x}% ${zoomPos.y}%`,
                    backgroundSize: "200%",
                  }}
                />
              )}
            </div>
          </div>

          {/* INFO SECTION */}
          <div className="product-info">
            <h1 className="text-3xl font-extrabold">
              {product.product_name}
            </h1>

            <p className="mt-3 text-slate-500">
              {product.description || "High quality product"}
            </p>

            <p className="text-2xl font-bold mt-6">
              ₹{product.price}
            </p>

            <div className="qty-control">
              <button onClick={() => setQty(Math.max(1, qty - 1))}>−</button>
              <span>{qty}</span>
              <button onClick={() => setQty(qty + 1)}>+</button>
            </div>

            <button className="btn btn-primary w-full mt-6" onClick={addToCart}>
              🛒 Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
