import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import './Details.css';

const STATUS_LABELS = {
  uploaded: 'Загружено',
  music_requested: 'Запрос музыки отправлен',
  music_generated: 'Музыка готова',
  music_failed: 'Ошибка генерации'
};

function Details() {
  const { id } = useParams();
  const [req, setReq] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDetails = () => {
    axios.get(`http://localhost:8080/api/queries/${id}`)
      .then(res => setReq(res.data))
      .catch(err => console.error(err));
  };

  useEffect(fetchDetails, [id]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`http://localhost:8080/api/queries/${id}/refresh`);
      fetchDetails();
    } catch (error) {
      const detail = error.response?.data?.detail;
      alert(detail ? `Не удалось обновить статус: ${detail}` : "Не удалось обновить статус");
    } finally {
      setRefreshing(false);
    }
  };

  if (!req) return <p>Загрузка...</p>;

  return (
    <div className="details-container">
      <h2>{req.title || 'Без названия'}</h2>
      <img
        src={`http://localhost:8080/api/image/${req.id}`}
        alt="Uploaded"
        className="details-image"
      />
      <p><strong>Стиль:</strong> {req.style || '—'}</p>
      <p><strong>Инструментальная:</strong> {req.instrumental ? 'Да' : 'Нет'}</p>
      {req.negative_tags && <p><strong>Исключить теги:</strong> {req.negative_tags}</p>}
      <h3>Промпт:</h3>
      <p>{req.prompt}</p>
      <h3>Статус:</h3>
      <p>{STATUS_LABELS[req.status] || req.status}</p>
      {req.suno_task_id && req.status !== 'music_generated' && (
        <button onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? 'Проверяю...' : 'Обновить статус'}
        </button>
      )}
      {req.music_details ? (
        <>
          <h3>Сгенерированная музыка:</h3>
          {req.music_details.map(track => (
            <div key={track.id} className="audio-container">
              <p><strong>{track.title}</strong> — {Math.round(track.duration)} сек.</p>
              <audio controls src={track.audio_url} />
              <br />
              <a className="download-link" href={track.audio_url} download={`music_${track.id}.mp3`}>
                Скачать
              </a>
            </div>
          ))}
        </>
      ) : req.status === 'music_failed' ? (
        <p>Генерация не удалась. Попробуйте запросить музыку ещё раз.</p>
      ) : (
        <p>Музыка ещё генерируется...</p>
      )}
    </div>
  );
}

export default Details;