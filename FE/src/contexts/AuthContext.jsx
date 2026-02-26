import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar usuario del localStorage al iniciar
    const storedUser = authService.getCurrentUser();
    if (storedUser) {
      console.log('🔐 Usuario cargado desde localStorage:', storedUser);
      console.log('🔐 Campañas del usuario:', storedUser.campanas);
      console.log('🔐 Inversionistas del usuario:', storedUser.inversionistas);
      setUser(storedUser);
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);
      console.log('🔐 Login exitoso - Datos del usuario:', response.user);
      console.log('🔐 Campañas asignadas:', response.user.campanas);
      console.log('🔐 Inversionistas asignados:', response.user.inversionistas);
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      setUser(response.user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const hasPermission = (permission) => {
    if (!user) return false;

    // Mapeo de permisos
    const permisos = {
      'torre_control': user.torre_control,
      'financiero': user.financiero,
      'recursos_humanos': user.recursos_humanos,
      'rrhh': user.recursos_humanos, // Alias
      'gestion_usuarios': user.gestion_usuarios,
      'gestion_metas': user.gestion_metas
    };

    return permisos[permission] === true;
  };

  const hasRole = (role) => {
    return user?.rol_nombre === role || false;
  };

  const value = {
    user,
    login,
    logout,
    hasPermission,
    hasRole,
    isAuthenticated: !!user,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
