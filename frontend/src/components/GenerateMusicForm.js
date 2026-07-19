import React, { useState } from 'react';
import axios from 'axios';
import ImageAnalysisPanel from './ImageAnalysisPanel';
import { EMOTION_STYLE_SUGGESTIONS } from '../emotionMeta';
import './GenerateMusic.css';

// Общая форма генерации музыки. Используется и на странице "/generate"
// сразу после загрузки (GenerateMusic.js), и на странице деталей для
// незавершённых черновиков (status === 'uploaded' в Details.js) - логика
// запроса одна и та же в обоих случаях (main.py /api/generate-music не
// различает "новую" и "старую" запись).
function GenerateMusicForm({ requestId, prompt, analysis, initialStyle = '', initialTitle = '', onGenerated }) {
  const [style, setStyle] = useState(initialStyle);
  const [title, setTitle] = useState(initialTitle);
  const [instrumental, setInstrumental] = useState(true);
  const [negativeTags, setNegativeTags] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const styleSuggestions = (analysis && EMOTION_STYLE_SUGGESTIONS[analysis.emotion]) || [];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!requestId || !style || !title) {
      alert("Заполните обязательные поля: стиль, название, и убедитесь, что загрузка прошла успешно.");
      return;
    }
    const formData = new FormData();
    formData.append('request_id', requestId);
    formData.append('style', style);
    formData.append('title', title);
    formData.append('instrumental', instrumental);
    formData.append('negative_tags', negativeTags);
    setSubmitting(true);
    try {
      await axios.post('http://localhost:8080/api/generate-music', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (onGenerated) onGenerated();
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail;
      alert(detail ? `Ошибка при генерации музыки: ${detail}` : "Ошибка при генерации музыки");
    } finally {
      setSubmitting(false);
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
      <ImageAnalysisPanel analysis={analysis} />
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Стиль (обязательно):</label>
          <input
            type="text"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            placeholder="Например, Classical, Jazz, Rock"
          />
          {styleSuggestions.length > 0 && (
            <div className="style-suggestions">
              <span className="style-suggestions-label">Предложено на основе анализа:</span>
              {styleSuggestions.map(s => (
                <button
                  type="button"
                  key={s}
                  className="style-chip"
                  onClick={() => setStyle(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}
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
        <button type="submit" disabled={submitting}>
          {submitting ? 'Отправляю...' : 'Создать мелодию'}
        </button>
      </form>
    </div>
  );
}

export default GenerateMusicForm;
