import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const DragDropUploader = ({ onFileUpload }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  
  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length) {
      setIsProcessing(true);
      try {
        await onFileUpload(acceptedFiles[0]);
      } finally {
        setIsProcessing(false);
      }
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'message/rfc822': ['.eml'],
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      {isProcessing ? (
        <p>Processing file...</p>
      ) : isDragActive ? (
        <p>Drop the file here...</p>
      ) : (
        <p>Drag & drop an email (.eml) or document here, or click to select</p>
      )}
    </div>
  );
};

export default DragDropUploader;