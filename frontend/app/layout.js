import "./globals.css";
import { Analytics } from "@vercel/analytics/react";

export const metadata = {
  title: "Job-Getter — Find remote jobs that match your CV",
  description:
    "Upload your CV and let AI research the web for remote roles that match your skills and experience. No account required.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>

        {children}
        <Analytics />

      </body>
    </html>
  );
}
