"use client";

import { useState } from "react";
import api from "../lib/api";
import { useRouter } from "next/navigation";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("/signup/", form);
      router.push(`/verify-otp?email=${form.email}`);
    } catch (err) {
      setError(err.response?.data?.error || "Signup failed");
    }
  };

  return (
    <div className="page-bg">
      <div className="card animate-card">
        <h2 className="title">Create Account</h2>
        <p className="subtitle">Join Cartsy today</p>

        {error && <div className="error animate-shake">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <input
            name="username"
            placeholder="Username"
            onChange={handleChange}
            required
          />

          <input
            name="email"
            type="email"
            placeholder="Email"
            onChange={handleChange}
            required
          />

          <input
            name="password"
            type="password"
            placeholder="Password"
            onChange={handleChange}
            required
          />

          <button type="submit">Create Account</button>
        </form>

        <p className="footer">
          Already have an account?{" "}
          <span onClick={() => router.push("/login")}>Login</span>
        </p>

        <style>{`
          :root {
            --brand: #4f46e5;
          }

          .page-bg {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(
              135deg,
              #0f172a,
              #020617,
              #020617
            );
            animation: bgMove 10s ease infinite;
          }

          @keyframes bgMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }

          .card {
            width: 100%;
            max-width: 400px;
            background: #ffffff;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.45);
          }

          .animate-card {
            animation: slideUp 0.6s ease forwards;
          }

          @keyframes slideUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            color: #020617;
          }

          .subtitle {
            text-align: center;
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
          }

          .form {
            margin-top: 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
          }

          input {
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #cbd5f5;
            font-size: 14px;
            outline: none;
            transition: 0.2s;
          }

          input:focus {
            border-color: var(--brand);
            box-shadow: 0 0 0 2px rgba(79,70,229,0.2);
          }

          button {
            margin-top: 8px;
            padding: 12px;
            border-radius: 10px;
            background: var(--brand);
            color: white;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: 0.2s;
          }

          button:hover {
            transform: translateY(-1px);
            filter: brightness(1.05);
          }

          .footer {
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
            color: #64748b;
          }

          .footer span {
            color: var(--brand);
            cursor: pointer;
            font-weight: 600;
          }

          .error {
            margin-top: 16px;
            background: #fee2e2;
            color: #b91c1c;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            text-align: center;
          }

          .animate-shake {
            animation: shake 0.35s;
          }

          @keyframes shake {
            0%,100% { transform: translateX(0); }
            25% { transform: translateX(-4px); }
            75% { transform: translateX(4px); }
          }
        `}</style>
      </div>
    </div>
  );
}
