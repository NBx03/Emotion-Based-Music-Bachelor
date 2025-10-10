import React, { useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import './GenerateMusic.css';

function GenerateMusic({ setNotification }) {
  const location = useLocation();
  const uploadData = location.state?.uploadData;
  // Получаем request_id и prompt из uploadData, полученных с предыдущей страницы
  const [requestId] = useState(uploadData ? uploadData.request_id : '');
  const [prompt] = useState(uploadData ? uploadData.prompt : '');
  const [style, setStyle] = useState('');
  const [title, setTitle] = useState('');
  const [instrumental, setInstrumental] = useState(true);
  const [negativeTags, setNegativeTags] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!requestId || !style || !title) {
      alert("Заполните обязательные поля: стиль, название, и убедитесь, что загрузка прошла успешно.");
      return;
    }
    // Отправляем request_id вместе с остальными параметрами на /api/generate-music
    const formData = new FormData();
    formData.append('request_id', requestId);
    formData.append('style', style);
    formData.append('title', title);
    formData.append('instrumental', instrumental);
    formData.append('negative_tags', negativeTags);
    try {
      const res = await axios.post('http://localhost:8080/api/generate-music', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatusMessage("Музыка генерируется...");
      // Можно использовать setTimeout или опрос API, чтобы позже показать уведомление о готовности музыки
      setTimeout(() => {
        setNotification("Генерация музыки завершена! Проверьте историю запросов.");
      }, 5000);
    } catch (error) {
      console.error(error);
      alert("Ошибка при генерации музыки");
    }
  };

  return (
    <div className="form-container">
      <h2>Генерация музыки</h2>
      {prompt && (
        <div className="result-container">
          <h3>Сгенерированный промпт:</h3>
          <p>{prompt}</p>
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Стиль (обязательно):</label>
          <input 
            type="text" 
            value={style} 
            onChange={(e) => setStyle(e.target.value)}
            placeholder="Например, Classical, Jazz, Rock" 
          />
        </div>
        <div className="form-group">
          <label>Название (обязательно):</label>
          <input 
            type="text" 
            value={title} 
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Название композиции" 
          />
        </div>
        <div className="form-group">
          <label>Инструментальная:</label>
          <select value={instrumental} onChange={(e) => setInstrumental(e.target.value === "true")}>
            <option value="true">Да</option>
            <option value="false">Нет</option>
          </select>
        </div>
        <div className="form-group">
          <label>Теги для исключения (необязательно):</label>
          <input 
            type="text" 
            value={negativeTags} 
            onChange={(e) => setNegativeTags(e.target.value)}
            placeholder="Например, Relaxing Piano" 
          />
        </div>
        <button type="submit">Создать мелодию</button>
      </form>
      {statusMessage && <p className="status-message">{statusMessage}</p>}
    </div>
  );
}

export default GenerateMusic;
