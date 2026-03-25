// src/routes.jsx
import { createBrowserRouter } from 'react-router-dom';
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
import PrivateRoute from './components/PrivateRoute';

console.log('Routes loaded');

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },
  {
    path: "/",
    element: <PrivateRoute><Root /></PrivateRoute>,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "products", element: <Products /> },
      { path: "products/:id", element: <ProductDetail /> },
      { path: "add-product", element: <AddProduct /> },
      { path: "analytics", element: <Analytics /> },
      { path: "profile", element: <Profile /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);