import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UploadModal.css';

function UploadModal({ onClose }) {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setError('');
  };

  // Превью выбранного файла до подтверждения загрузки
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return undefined;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Выберите изображение");
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      // Используем абсолютный URL; убедитесь, что backend доступен по этому адресу
      const response = await axios.post('http://localhost:8080/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Ожидается, что ответ содержит request_id, prompt и analysis
      const uploadData = {
         request_id: response.data.request_id,
         prompt: response.data.prompt,
         analysis: response.data.analysis
      };
      // Переходим на страницу генерации музыки с передачей данных uploadData
      navigate('/generate', { state: { uploadData } });
      onClose();
    } catch (err) {
      console.error(err);
      setError("Ошибка при загрузке изображения");
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Загрузить изображение</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          {previewUrl && (
            <div className="upload-preview">
              <img src={previewUrl} alt="Предпросмотр" />
            </div>
          )}
          <div className="modal-buttons">
            <button type="submit">Загрузить</button>
            <button type="button" onClick={onClose}>Отмена</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default UploadModal;
