import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import GenerateMusicForm from './GenerateMusicForm';

function GenerateMusic() {
  const location = useLocation();
  const navigate = useNavigate();
  const uploadData = location.state?.uploadData;
  const requestId = uploadData ? uploadData.request_id : '';
  const prompt = uploadData ? uploadData.prompt : '';
  const analysis = uploadData ? uploadData.analysis : null;

  return (
    <GenerateMusicForm
      requestId={requestId}
      prompt={prompt}
      analysis={analysis}
      onGenerated={() => navigate(`/details/${requestId}`)}
    />
  );
}

export default GenerateMusic;
