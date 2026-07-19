import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import FloatingUploadButton from './components/FloatingUploadButton';
import UploadModal from './components/UploadModal';
import GenerateMusic from './components/GenerateMusic';
import History from './components/History';
import Details from './components/Details';
import Analytics from './components/Analytics';
import Notification from './components/Notification';
import './App.css';

function App() {
  const [isUploadModalOpen, setUploadModalOpen] = useState(false);
  const [notification, setNotification] = useState(null);

  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<History />} />
            <Route path="/generate" element={<GenerateMusic />} />
            <Route path="/history" element={<History />} />
            <Route path="/details/:id" element={<Details />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<History />} />
          </Routes>
        </main>
        <FloatingUploadButton onClick={() => setUploadModalOpen(true)} />
        {isUploadModalOpen && <UploadModal onClose={() => setUploadModalOpen(false)} />}
        {notification && <Notification message={notification} onClose={() => setNotification(null)} />}
      </div>
    </Router>
  );
}

export default App;
