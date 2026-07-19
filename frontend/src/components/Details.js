import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import ImageAnalysisPanel from './ImageAnalysisPanel';
import GenerateMusicForm from './GenerateMusicForm';
import './Details.css';

const STATUS_LABELS = {
  uploaded: 'Загружено',
  music_requested: 'Запрос музыки отправлен',
  music_generated: 'Музыка готова',
  music_failed: 'Ошибка генерации'
};

const POLL_INTERVAL_MS = 7000;

function Details() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [req, setReq] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDetails = useCallback(() => {
    return axios.get(`http://localhost:8080/api/queries/${id}`)
      .then(res => setReq(res.data))
      .catch(err => console.error(err));
  }, [id]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  // B1: пока Suno обрабатывает запрос - опрашиваем статус сами, вебхук
  // без публичного callBackUrl (ngrok) до нас не достучится
  useEffect(() => {
    if (req?.status !== 'music_requested') {
      return undefined;
    }
    const intervalId = setInterval(fetchDetails, POLL_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [req?.status, fetchDetails]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`http://localhost:8080/api/queries/${id}/refresh`);
      await fetchDetails();
    } catch (error) {
      const detail = error.response?.data?.detail;
      alert(detail ? `Не удалось обновить статус: ${detail}` : "Не удалось обновить статус");
    } finally {
      setRefreshing(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Удалить этот запрос? Действие необратимо.')) return;
    try {
      await axios.delete(`http://localhost:8080/api/queries/${id}`);
      navigate('/history');
    } catch (error) {
      console.error(error);
      alert('Не удалось удалить запрос');
    }
  };

  if (!req) return <p>Загрузка...</p>;

  const isDraft = req.status === 'uploaded';

  return (
    <div className="details-container">
      <h2>{req.title || 'Без названия'}</h2>
      <img
        src={`http://localhost:8080/api/image/${req.id}`}
        alt="Uploaded"
        className="details-image"
      />

      {isDraft ? (
        // B2: загрузка завершена, но стиль/название ещё не заполнены - та же
        // форма, что и сразу после /api/upload, только предзаполненная
        <>
          <p className="draft-notice">
            Черновик — фото загружено, но музыка ещё не запрошена. Заполните форму ниже, чтобы продолжить.
          </p>
          <GenerateMusicForm
            requestId={req.id}
            prompt={req.prompt}
            analysis={req.analysis_result}
            initialStyle={req.style}
            initialTitle={req.title}
            onGenerated={fetchDetails}
          />
        </>
      ) : (
        <>
          <p><strong>Стиль:</strong> {req.style || '—'}</p>
          <p><strong>Инструментальная:</strong> {req.instrumental ? 'Да' : 'Нет'}</p>
          {req.negative_tags && <p><strong>Исключить теги:</strong> {req.negative_tags}</p>}
          <ImageAnalysisPanel analysis={req.analysis_result} />
          <h3>Промпт:</h3>
          <p>{req.prompt}</p>
          <h3>Статус:</h3>
          <p>{STATUS_LABELS[req.status] || req.status}</p>
          {req.status === 'music_requested' && (
            <p className="polling-notice">Статус обновляется автоматически, обновлять страницу не нужно...</p>
          )}
          {req.suno_task_id && req.status !== 'music_generated' && (
            <button onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? 'Проверяю...' : 'Обновить статус'}
            </button>
          )}
          {req.music_details ? (
            <>
              <h3>Сгенерированная музыка:</h3>
              {req.music_details.map((track, index) => (
                <div key={track.id} className="audio-container">
                  <p>
                    <strong>{track.title}</strong>
                    {req.music_details.length > 1 ? ` (Вариант ${index + 1})` : ''}
                    {' — '}{Math.round(track.duration)} сек.
                  </p>
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
        </>
      )}

      <button className="delete-button" onClick={handleDelete}>Удалить запрос</button>
    </div>
  );
}

export default Details;
