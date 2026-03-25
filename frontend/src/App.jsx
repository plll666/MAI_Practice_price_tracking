// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Root from './pages/Root';
import Dashboard from './pages/Dashboard/Dashboard';
import Products from './pages/Products/Products';
import ProductDetail from './pages/ProductDetail/ProductDetail';
import AddProduct from './pages/AddProduct/AddProduct';
import Analytics from './pages/Analytics/Analytics';
import Profile from './pages/Profile/Profile';
import Settings from './pages/Settings/Settings';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={user ? <Root /> : <Navigate to="/login" replace />}
      >
        <Route index element={<Dashboard />} />
        <Route path="products" element={<Products />} />
        <Route path="products/:id" element={<ProductDetail />} />
        <Route path="add-product" element={<AddProduct />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;