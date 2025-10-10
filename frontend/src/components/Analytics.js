// Analytics.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Analytics.css';

function Analytics() {
  const metrics = {
    totalRequests: 62,
    popularStyle: 'Джаз',
    avgTime: '56 сек.'
  };

  const emotions = [
    { label: 'Умиротворённость', value: 27.4, color: '#4caf50' },
    { label: 'Восхищение',       value: 22.5, color: '#ff9800' },
    { label: 'Печаль',           value: 16.1, color: '#2196f3' },
    { label: 'Гнев',             value: 12.9, color: '#f44336' },
    { label: 'Возбуждение',      value: 8,    color: '#9c27b0' },
    { label: 'Благоговение',     value: 4.8,  color: '#00bcd4' },
    { label: 'Страх',            value: 4.8,  color: '#795548' },
    { label: 'Отвращение',       value: 3.2,  color: '#8bc34a' }
  ];

  return (
    <div className="analytics-page">
      <div className="analytics-container">
        <h2>Панель аналитики</h2>
        <div className="analytics-metrics">
          <div className="analytics-card">
            <div className="card-header">Всего запросов</div>
            <div className="card-value">{metrics.totalRequests}</div>
          </div>
          <div className="analytics-card">
            <div className="card-header">Самый популярный стиль</div>
            <div className="card-value">{metrics.popularStyle}</div>
          </div>
          <div className="analytics-card">
            <div className="card-header">Среднее время генерации</div>
            <div className="card-value">{metrics.avgTime}</div>
          </div>
        </div>

        <div className="analytics-emotions">
          <h3>Распределение запросов по эмоциям</h3>
          {emotions.map(em => (
            <div key={em.label} className="emotion-row">
              <div className="emotion-bar-label">{em.label}</div>
              <div className="emotion-bar-container">
                <div
                  className="emotion-bar-fill"
                  style={{ width: `${em.value}%`, backgroundColor: em.color }}
                />
              </div>
              <div className="emotion-bar-percentage">{em.value}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Analytics;
