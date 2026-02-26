import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DashboardRedirect = () => {
  const { user } = useAuth();

  // Redirigir al primer tablero disponible según permisos
  if (user?.permisos?.torre_de_control) {
    return <Navigate to="/kpi" replace />;
  }
  
  if (user?.permisos?.financiero) {
    return <Navigate to="/financiero" replace />;
  }
  
  if (user?.permisos?.recursos_humanos) {
    return <Navigate to="/talento" replace />;
  }

  // Si no tiene ningún permiso, mostrar mensaje
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '60vh',
      textAlign: 'center'
    }}>
      <h2>Sin Acceso</h2>
      <p>No tienes permisos asignados para acceder a ningún tablero.</p>
      <p>Contacta al administrador del sistema.</p>
    </div>
  );
};

export default DashboardRedirect;
