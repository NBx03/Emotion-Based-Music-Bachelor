// Единый источник правды для отображения эмоций EmoSet на русском и
// подсказок стиля по эмоции. Английские ключи приходят из backend
// (image_processing.py / image_analysis.py). Русские подписи взяты из
// уже существовавших меток на странице "Аналитика" (Analytics.js).
export const EMOTION_LABELS = {
  amusement: 'Восхищение',
  anger: 'Гнев',
  awe: 'Благоговение',
  contentment: 'Умиротворённость',
  disgust: 'Отвращение',
  excitement: 'Возбуждение',
  fear: 'Страх',
  sadness: 'Печаль',
};

export const EMOTION_STYLE_SUGGESTIONS = {
  amusement: ['Pop', 'Upbeat'],
  anger: ['Rock', 'Industrial'],
  awe: ['Cinematic', 'Ambient'],
  contentment: ['Acoustic', 'Chill'],
  disgust: ['Experimental', 'Dark Ambient'],
  excitement: ['EDM', 'Dance'],
  fear: ['Horror Score', 'Dark Ambient'],
  sadness: ['Piano', 'Ambient'],
};

export function emotionLabel(emotion) {
  return EMOTION_LABELS[emotion] || emotion;
}
