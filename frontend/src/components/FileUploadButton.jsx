import { useRef, useState } from 'react';
import { fileApi } from '../services/fileApi';

const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg'];
const MAX_SIZE = 20 * 1024 * 1024; // 20MB

export default function FileUploadButton({ sessionId, onUploadStart, onUploadComplete, onUploadError }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate size
    if (file.size > MAX_SIZE) {
      if (onUploadError) onUploadError("File size exceeds 20MB limit.");
      return;
    }

    // Validate extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
      if (onUploadError) onUploadError(`Invalid file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`);
      return;
    }

    setIsUploading(true);
    if (onUploadStart) onUploadStart(file);

    try {
      const data = await fileApi.uploadFile(sessionId, file);
      if (onUploadComplete) onUploadComplete(data);
    } catch (err) {
      console.error("Upload error", err);
      if (onUploadError) onUploadError(err.response?.data?.detail || "Failed to upload file");
    } finally {
      setIsUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="relative flex items-center justify-center">
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange}
        className="hidden" 
        accept=".pdf,.png,.jpg,.jpeg"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        className={`p-2 rounded-lg text-slate-400 hover:text-blue-500 hover:bg-slate-800 transition-colors ${
          isUploading ? 'opacity-50 cursor-not-allowed animate-pulse' : ''
        }`}
        title="Upload File (PDF, PNG, JPG - max 20MB)"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
      </button>
    </div>
  );
}
