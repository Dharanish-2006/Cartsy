import { Suspense } from "react";
import VerifyOTPClient from "./VerifyOtpClient"

export default function VerifyOTPPage() {
  return (
    <div className="page-bg">
      <div className="home-wrapper">
        <Suspense fallback={<div className="text-white">Loading...</div>}>
          <VerifyOTPClient />
        </Suspense>
      </div>
    </div>
  );
}
