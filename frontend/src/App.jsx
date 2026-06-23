import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import PredictPage from './pages/PredictPage';
import AnalyticsPage from './pages/AnalyticsPage';
import HeatmapPage from './pages/HeatmapPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/heatmap" element={<HeatmapPage />} />
      </Routes>
    </Layout>
  );
}

export default App;