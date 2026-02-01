"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../lib/api";
import Image from "next/image";
import { loadRazorpay } from "../lib/loadRazorpay";

export default function CheckoutPage() {
  const router = useRouter();

  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const [paymentMethod, setPaymentMethod] = useState("COD");

  const [address, setAddress] = useState({
    full_name: "",
    address: "",
    city: "",
    postal_code: "",
    country: "",
  });

  useEffect(() => {
    const token = localStorage.getItem("access");
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await api.get("cart/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setCart(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setAddress({ ...address, [e.target.name]: e.target.value });
  };

  const placeOrder = async () => {
    try {
      if (
        !address.full_name ||
        !address.address ||
        !address.city ||
        !address.postal_code ||
        !address.country
      ) {
        alert("Please fill all shipping details");
        return;
      }

      const token = localStorage.getItem("access");

      /* ---------- CASH ON DELIVERY ---------- */
      if (paymentMethod === "COD") {
        await api.post(
          "orders/create/",
          {
            full_name: address.full_name,
            address: address.address,
            city: address.city,
            postal_code: address.postal_code,
            country: address.country,
            payment_method: "COD",
            total_amount: total,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );

        router.push("/orders");
        return;
      }

      /* ---------- RAZORPAY ---------- */
      if (paymentMethod === "ONLINE") {
        const loaded = await loadRazorpay();

        if (!loaded) {
          alert("Razorpay SDK failed to load");
          return;
        }

        const token = localStorage.getItem("access");

        const res = await api.post(
          "orders/razorpay/",
          {
            ...address,
          },
          { headers: { Authorization: `Bearer ${token}` } },
        );

        const options = {
          key: res.data.key,
          amount: res.data.amount,
          currency: "INR",
          name: "Cartsy",
          description: "Order Payment",
          order_id: res.data.order_id,
          handler: function () {
            router.push("/orders");
          },
          theme: {
            color: "#4f46e5",
          },
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
      }
    } catch (err) {
      console.log(err);
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
        </div>
      </div>

      <div className="home-wrapper">
        <div className="card home-card grid grid-cols-1 md:grid-cols-12 gap-10">
          <div className="md:col-span-7">
            <h3 className="text-xl font-bold mb-4">📦 Shipping Details</h3>

            <div className="space-y-4">
              <input
                className="input"
                name="full_name"
                placeholder="Full Name"
                onChange={handleChange}
              />
              <textarea
                className="input"
                name="address"
                placeholder="Address"
                rows={3}
                onChange={handleChange}
              />
              <input
                className="input"
                name="city"
                placeholder="City"
                onChange={handleChange}
              />

              <div className="grid grid-cols-2 gap-4">
                <input
                  className="input"
                  name="postal_code"
                  placeholder="Postal Code"
                  onChange={handleChange}
                />
                <input
                  className="input"
                  name="country"
                  placeholder="Country"
                  onChange={handleChange}
                />
              </div>

              <h4 className="font-semibold mt-6">💳 Payment Method</h4>

              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={paymentMethod === "COD"}
                  onChange={() => setPaymentMethod("COD")}
                />
                Cash on Delivery
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={paymentMethod === "ONLINE"}
                  onChange={() => setPaymentMethod("ONLINE")}
                />
                Pay with Razorpay
              </label>
            </div>
          </div>
          <div className="md:col-span-5">
            <h3 className="text-xl font-bold mb-4">🛒 Order Summary</h3>

            <ul className="space-y-4">
              {cart.map((item) => (
                <li
                  key={item.id}
                  className="flex justify-between items-center border-b pb-3"
                >
                  <div>
                    <strong>{item.product.product_name}</strong>
                    <div className="text-sm text-gray-500">
                      Qty: {item.quantity}
                    </div>
                  </div>
                  <span>₹{item.product.price * item.quantity}</span>
                </li>
              ))}

              <li className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span className="text-[rgb(var(--brand))]">₹{total}</span>
              </li>
            </ul>

            <button
              onClick={placeOrder}
              className="btn btn-primary w-full mt-6 py-3 text-lg"
            >
              Place Order →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
