import { createContext, useState } from 'react';

export const UploadContext = createContext();

export function UploadProvider({ children }) {
  const [uploadData, setUploadData] = useState({ file: null, request: null });
  return (
    <UploadContext.Provider value={{ uploadData, setUploadData }}>
      {children}
    </UploadContext.Provider>
  );
}
