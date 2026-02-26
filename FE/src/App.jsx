import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import esES from 'antd/locale/es_ES';
import dayjs from 'dayjs';
import 'dayjs/locale/es';
import { AuthProvider } from './contexts/AuthContext';
import { DiasLaborablesProvider } from './contexts/DiasLaborablesContext';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardRedirect from './components/DashboardRedirect';
import Login from './pages/Login';
import MainLayout from './layouts/MainLayout';
import KpiTablero from './pages/KpiTablero';
import TableroFinanciero from './pages/TableroFinanciero';
import TableroTalentoHumano from './pages/TableroTalentoHumano';
import RadarTalento from './pages/RadarTalento';
import Tesoreria from './pages/Tesoreria';
import GestionMetas from './pages/GestionMetas';
import GestionPermisos from './pages/GestionPermisos';

// Configurar dayjs en español globalmente
dayjs.locale('es');

function App() {
  return (
    <ConfigProvider locale={esES}>
      <AuthProvider>
        <DiasLaborablesProvider>
          <Router>
            <Routes>
              {/* Ruta pública */}
              <Route path="/login" element={<Login />} />

              {/* Rutas protegidas */}
              <Route path="/" element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }>
                <Route index element={<DashboardRedirect />} />
                <Route path="dashboard" element={<DashboardRedirect />} />

                <Route path="kpi" element={
                  <ProtectedRoute requiredPermission="torre_control">
                    <KpiTablero />
                  </ProtectedRoute>
                } />

                <Route path="financiero" element={
                  <ProtectedRoute requiredPermission="financiero">
                    <TableroFinanciero />
                  </ProtectedRoute>
                } />

                <Route path="talento" element={
                  <ProtectedRoute requiredPermission="recursos_humanos">
                    <TableroTalentoHumano />
                  </ProtectedRoute>
                } />

                <Route path="tesoreria" element={
                  <ProtectedRoute requiredPermission="torre_control">
                    <Tesoreria />
                  </ProtectedRoute>
                } />

                <Route path="radar-talento" element={
                  <ProtectedRoute requiredPermission="recursos_humanos">
                    <RadarTalento />
                  </ProtectedRoute>
                } />

                <Route path="gestion-metas" element={<GestionMetas />} />
                <Route path="permisos" element={<GestionPermisos />} />
              </Route>

              {/* Redirigir rutas desconocidas al login */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Router>
        </DiasLaborablesProvider>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
