"use client";

import { useState } from "react";
import api from "../lib/api";
import { useRouter, useSearchParams } from "next/navigation";

export default function VerifyOTPPage() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email");

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  const submitOTP = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("/verify-otp/", { email, otp });
      router.push("/login");
    } catch (err) {
      setError(err.response?.data?.error || "Invalid OTP");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={submitOTP} className="w-80 space-y-4">
        <h2 className="text-xl font-bold">Verify OTP</h2>

        {error && <p className="text-red-500">{error}</p>}

        <input
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          required
          className="input"
        />

        <button className="btn w-full">Verify</button>
      </form>
    </div>
  );
}
