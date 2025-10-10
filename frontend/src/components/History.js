import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './History.css';

const STATUS_LABELS = {
  uploaded: 'Загружено',
  music_requested: 'Запрос музыки отправлен',
  music_generated: 'Музыка готова'
};

function History() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8080/api/queries')
      .then(res => setRequests(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="history-container">
      <h2>История запросов</h2>
      <ul className="history-list">
        {requests.map(req => (
          <li key={req.id} className="history-item">
            <img
              src={`http://localhost:8080/api/image/${req.id}`}
              alt="Uploaded"
              className="thumbnail"
            />
            <div className="history-info">
              <h3 className="request-title">{req.title || 'Без названия'}</h3>
              <p><strong>Стиль:</strong> {req.style || '—'}</p>
              <p><strong>Статус:</strong> {STATUS_LABELS[req.status] || req.status}</p>
              <Link to={`/details/${req.id}`} className="details-button">
                Смотреть детали
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default History;