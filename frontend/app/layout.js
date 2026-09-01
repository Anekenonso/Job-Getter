export const metadata = {
  title: "Job-Getter",
  description: "Find remote jobs that match your CV",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
