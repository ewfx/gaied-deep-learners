import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';

function FileUpload() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'message/rfc822': ['.eml'],
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    onDrop: async acceptedFiles => {
      if (acceptedFiles.length) {
        setLoading(true);
        const formData = new FormData();
        formData.append('file', acceptedFiles[0]);

        try {
          const response = await fetch('http://localhost:8000/process-email', {
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          setResult(data);
        } catch (error) {
          console.error(error);
        } finally {
          setLoading(false);
        }
      }
    }
  });

  return (
    <div>
      <div {...getRootProps()} style={dropzoneStyle}>
        <input {...getInputProps()} />
        <p>Drag & drop an .eml or PDF file here, or click to select</p>
      </div>
      
      {loading && <p>Processing...</p>}
      
      {result && (
        <div style={resultStyle}>
          <h3>Classification Results</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

const dropzoneStyle = {
  border: '2px dashed #0087F7',
  borderRadius: '4px',
  padding: '20px',
  textAlign: 'center',
  cursor: 'pointer',
  margin: '20px 0'
};

const resultStyle = {
  marginTop: '20px',
  padding: '15px',
  backgroundColor: '#f5f5f5',
  borderRadius: '4px'
};

export default FileUpload;