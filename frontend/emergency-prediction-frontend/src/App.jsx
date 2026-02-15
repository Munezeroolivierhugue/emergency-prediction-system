import Header from "./components/Header";
import Footer from "./components/Footer";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex-grow">
        <AppRoutes />
      </div>
      <Footer />
    </div>
  );
}

export default App;
