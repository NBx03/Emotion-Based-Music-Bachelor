import React from 'react';
import './FloatingUploadButton.css';

function FloatingUploadButton({ onClick }) {
  return (
    <button className="floating-upload-button" onClick={onClick}>
      Загрузить
    </button>
  );
}

export default FloatingUploadButton;
