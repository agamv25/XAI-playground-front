'use client'
import { useState } from 'react';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import './entry.css';

const Entry = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setUploadStatus('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            setUploadStatus('Uploading...');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                setUploadStatus('Upload completed successfully!');
            } else {
                setUploadStatus('Upload failed');
            }
        } catch (error) {
            setUploadStatus('Error occurred during upload');
            console.error('Upload error:', error);
        }
    };

    return (
        <div>
            <div className="Text">
                <h2>No analysis yet</h2>
                <p>Upload your data and model to explore explainability techniques: SHAP, LIME, feature importance, and saliency maps.</p>
            </div>
            <div className="data-entry">
                <Button
                    component="label"
                    variant="contained"
                    tabIndex={-1}
                    startIcon={<CloudUploadIcon />}
                >
                    Select CSV File
                    <input
                        type="file"
                        className="visually-hidden-input"
                        onChange={handleFileSelect}
                        accept=".csv"
                    />
                </Button>
                {selectedFile && <p style={{ marginLeft: '1rem' }}>{selectedFile.name}</p>}

                <Button
                    variant="contained"
                    onClick={handleUpload}
                    style={{ marginLeft: '1rem' }}
                >
                    Upload
                </Button>
            </div>
            {uploadStatus && <p>{uploadStatus}</p>}
        </div>
    );
};

export default Entry;