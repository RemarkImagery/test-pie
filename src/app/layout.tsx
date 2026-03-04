export const metadata = {
  title: "Test Pie",
  description: "Webflow Cloud code components for NZ Pie Review",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
