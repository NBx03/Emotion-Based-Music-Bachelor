import React from 'react';
import { emotionLabel } from '../emotionMeta';
import './ImageAnalysisPanel.css';

function AnalysisBar({ label, value }) {
  const percent = Math.round((value || 0) * 100);
  return (
    <div className="analysis-bar-row">
      <div className="analysis-bar-label">{label}</div>
      <div className="analysis-bar-container">
        <div className="analysis-bar-fill" style={{ width: `${percent}%` }} />
      </div>
      <div className="analysis-bar-percentage">{percent}%</div>
    </div>
  );
}

function ImageAnalysisPanel({ analysis }) {
  if (!analysis) return null;

  const objects = analysis.objects || [];

  return (
    <div className="analysis-panel">
      <h3>Анализ изображения</h3>
      <div className="analysis-emotion">
        <span className="analysis-emotion-label">Эмоция:</span>{' '}
        <span className="analysis-emotion-value">{emotionLabel(analysis.emotion)}</span>
      </div>
      <AnalysisBar label="Яркость" value={analysis.brightness} />
      <AnalysisBar label="Насыщенность цвета" value={analysis.colorfulness} />
      <div className="analysis-faces">
        <strong>Лица на фото:</strong> {analysis.face_count > 0 ? analysis.face_count : 'не обнаружено'}
      </div>
      {objects.length > 0 && (
        <div className="analysis-objects">
          <strong>Объекты:</strong>
          <div className="analysis-chips">
            {objects.map((obj, i) => (
              <span key={`${obj}-${i}`} className="analysis-chip">{obj}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageAnalysisPanel;
