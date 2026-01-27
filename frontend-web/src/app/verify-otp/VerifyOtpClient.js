"use client";

import { useState } from "react";
import api from "../lib/api";
import { useRouter, useSearchParams } from "next/navigation";

export default function VerifyOTPClient() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email");

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submitOTP = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/verify-otp/", { email, otp });
      router.push("/login");
    } catch (err) {
      setError(err.response?.data?.error || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card home-card max-w-sm w-full animate-card">
      <h2 className="text-2xl font-extrabold text-center mb-2">
        Verify OTP
      </h2>

      <p className="text-sm text-gray-500 text-center mb-6">
        OTP sent to <span className="font-medium">{email}</span>
      </p>

      {error && (
        <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <form onSubmit={submitOTP} className="space-y-4">
        <input
          type="text"
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          required
          className="input text-center tracking-widest"
        />

        <button
          disabled={loading}
          className="btn btn-primary w-full py-3"
        >
          {loading ? "Verifying..." : "Verify OTP"}
        </button>
      </form>
    </div>
  );
}
