import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PrintPage from './pages/PrintPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/print/*" element={<PrintPage />} />
        <Route path="/" element={<PrintPage />} />
      </Routes>
    </Router>
  );
}

export default App;