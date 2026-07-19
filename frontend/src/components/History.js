import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './History.css';

const STATUS_LABELS = {
  uploaded: 'Загружено',
  music_requested: 'Запрос музыки отправлен',
  music_generated: 'Музыка готова',
  music_failed: 'Ошибка генерации'
};

function History() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8080/api/queries')
      .then(res => setRequests(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить этот запрос?')) return;
    try {
      await axios.delete(`http://localhost:8080/api/queries/${id}`);
      setRequests(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      console.error(err);
      alert('Не удалось удалить запрос');
    }
  };

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
              <button className="history-delete-button" onClick={() => handleDelete(req.id)}>
                Удалить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default History;